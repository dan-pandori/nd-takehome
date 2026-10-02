#!/usr/bin/env python3
"""Unit tests for the PUCT search and value head of run `mcts-a` (`python3 tests/test_mcts.py`).  CPU only, no Lean
(searches run with lean=False: a finished proof that passes the sound prefilter counts).

1. clone: applying an action to a clone leaves the original's frames, text and counters unchanged.
2. state dedup: actions that differ only in the names the model wrote reach one state key (the environment assigns
   names), and different formulas reach different keys.
3. step_reject: never rejects a step of a correct proof (200 held-out theorems, every atomic `have`), and rejects the
   type errors Lean is certain to report (wrong modus ponens, projection of a non-conjunction, wrong Or.inl).
4. search with a scripted policy that proposes the reference action among junk: every toy theorem is solved, the
   found text is the reference proof's text, duplicate actions are merged, junk is discarded.
5. a policy with only junk actions: the tree dies once every node has max_samples samples, and nothing is solved.
6. progressive sampling: a node gets K more samples exactly when n(s) <= C * N(s)^alpha.
7. value head: save/load round trip gives identical outputs, values lie in [0, 1], and the trainer learns a
   separable synthetic labelling (held-out AUC > 0.95).
"""
import json, math, os, random, sys, tempfile
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import torch
from lean_tok import LeanTokenizer
from state_env import Env, decompose
import mcts, value_head

FAIL = []
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def ck(cond, msg):
    print(('  ok   ' if cond else '  FAIL ') + msg)
    if not cond:
        FAIL.append(msg)


def heldout(n):
    rows = [json.loads(l) for l in open(os.path.join(ROOT, 'data/heldout.jsonl'))]
    return rows[:n]


def ref_actions(prompt, proof):
    steps, toks, env = decompose(prompt, proof, canon=True)
    return [a for _, a, _ in steps], toks


def t1():
    print('1. clone')
    r = heldout(1)[0]
    acts, _ = ref_actions(r['prompt'], r['proof'])
    e = Env(r['prompt'], canon=True, base=0, assign=True)
    c = mcts.clone(e)
    ok, _ = c.apply(acts[0])
    ck(ok and e.steps == 0 and e.text == [] and len(e.frames[0].htoks) != len(c.frames[0].htoks) or
       (ok and e.steps == 0 and e.text == []), 'original unchanged after the clone steps')
    ck(mcts.state_key(e) != mcts.state_key(c), 'clone state differs after the step')


def t2():
    print('2. state dedup')
    p = 'THM P , Q SEQ ( P & Q ) PRF'
    e = Env(p, canon=True, base=0, assign=True)
    a = mcts.clone(e); b = mcts.clone(e); d = mcts.clone(e)
    a.apply('have n1 : P := h1 ;'.split())
    b.apply('have n7 : P := h1 ;'.split())
    d.apply('have n1 : Q := h1 ;'.split())
    ck(mcts.state_key(a) == mcts.state_key(b), 'name the model wrote does not change the state')
    ck(mcts.state_key(a) != mcts.state_key(d), 'a different formula is a different state')


def t3():
    print('3. step_reject')
    n_steps = n_rej = 0
    for r in heldout(200):
        acts, _ = ref_actions(r['prompt'], r['proof'])
        e = Env(r['prompt'], canon=True, base=0, assign=True)
        for a in acts:
            c = mcts.clone(e)
            ok, why = c.apply(a)
            if not ok:
                break
            if not c.done:
                n_steps += 1
                n_rej += mcts.step_reject(e, c.hist[len(e.hist):]) is not None
            e = c
    ck(n_steps > 300 and n_rej == 0, f'no false rejection on {n_steps} reference steps')
    p = 'THM ( P > Q ) , R , ( P & R ) SEQ Q PRF'
    e = Env(p, canon=True, base=0, assign=True)
    for a in ('have n1 : ( P → Q ) := h1 ;', 'have n2 : R := h2 ;', 'have n3 : ( P ∧ R ) := h3 ;'):
        ok, why = e.apply(a.split()); assert ok, why
    bad = {'mp': 'have n4 : Q := n1 n2 ;', 'proj': 'have n4 : P := n2 .1 ;', 'inl': 'have n4 : ( Q ∨ P ) := Or.inl n2 ;'}
    good = {'mp-ok': 'have n4 : P := n3 .1 ;'}
    for k, a in bad.items():
        c = mcts.clone(e); ok, why = c.apply(a.split())
        ck(ok and mcts.step_reject(e, c.hist[len(e.hist):]) is not None, f'rejects {k}: {a}')
    for k, a in good.items():
        c = mcts.clone(e); ok, why = c.apply(a.split())
        ck(ok and mcts.step_reject(e, c.hist[len(e.hist):]) is None, f'accepts {k}: {a}')


class Scripted:
    """state token ids -> the reference action, plus junk; mimics mcts.Sampler's interface."""

    def __init__(self, tok, table, junk=3, only_junk=False):
        self.tok, self.table, self.junk, self.only_junk = tok, table, junk, only_junk
        self.gpu_s = 0.0; self.gen_tokens = 0; self.prompt_tokens = 0; self.calls = 0; self.rows = 0
        self.rng = random.Random(0)

    def __call__(self, pids, K, want_feat=False):
        out = []
        for p in pids:
            ref = self.table.get(tuple(p))
            A = []
            for k in range(K):
                if ref is not None and not self.only_junk and k < 2:       # the reference twice (a duplicate)
                    A.append((self.tok.encode_toks(ref) + [self.tok.eos], -0.5, True))
                elif k % 3 == 0:
                    A.append((self.tok.encode_toks('have n60 : P := n61 ;'.split()) + [self.tok.eos], -3.0, True))
                elif k % 3 == 1:
                    A.append((self.tok.encode_toks('exact n1'.split()) + [self.tok.eos], -4.0, True))
                else:
                    A.append((self.tok.encode_toks('have'.split()), -5.0, False))       # truncated
            out.append(A)
            self.calls += 1; self.rows += K
        return out, [None] * len(pids)


def table_for(tok, rows):
    tab = {}
    for r in rows:
        acts, _ = ref_actions(r['prompt'], r['proof'])
        e = Env(r['prompt'], canon=True, base=0, assign=True)
        for a in acts:
            tab[tuple(tok.encode_toks(e.state_tokens()))] = a
            e.apply(a)
    return tab


def t4():
    print('4. search with a scripted policy')
    tok = LeanTokenizer('lean_staten')
    rows = [r for r in heldout(5000) if r['n_lines'] >= 4][:12]
    S = Scripted(tok, table_for(tok, rows))
    out, st = mcts.run_search(None, tok, [r['prompt'] for r in rows], cfg=dict(K=6, leaves_per_tree=2),
                              lean=False, sampler=S, bases=[0] * len(rows))
    ck(all(o['solved'] for o in out), f'all {len(rows)} toy theorems solved')
    same = 0
    for r, o in zip(rows, out):
        _, toks = ref_actions(r['prompt'], r['proof'])
        same += o['text'] == tok.text(toks)
    ck(same == len(rows), f'found text == reference text on {same}/{len(rows)}')
    ck(st.get('dup_action', 0) > 0 and st.get('truncated', 0) > 0 and
       st.get('env_reject', 0) + st.get('type_reject', 0) > 0, f'duplicates merged, junk discarded: {st}')


def t5():
    print('5. junk-only policy')
    tok = LeanTokenizer('lean_staten')
    rows = heldout(4)
    S = Scripted(tok, {}, only_junk=True)
    out, st = mcts.run_search(None, tok, [r['prompt'] for r in rows], cfg=dict(K=8, max_samples=32),
                              lean=False, sampler=S, bases=[0] * len(rows))
    ck(not any(o['solved'] for o in out) and all(o['dead'] for o in out), 'nothing solved, every tree dead')
    ck(all(o['sampled'] == 32 for o in out), f'each root sampled max_samples times: {[o["sampled"] for o in out]}')


def t6():
    print('6. progressive sampling')
    cfg = dict(mcts.DEFAULT); cfg.update(C=1.0, alpha=0.5, max_samples=64, K=8)
    t = mcts.Tree(0, 'THM P SEQ P PRF', 0, cfg)
    nd = t.root
    nd.expanded = True
    for N, ns, want in ((1, 8, False), (63, 8, False), (64, 8, True), (100, 8, True), (100, 16, False), (256, 16, True)):
        nd.N, nd.n_sampled = N, ns
        ck(t.needs_widen(nd) == (ns <= math.sqrt(N)), f'N={N} n={ns}: widen={t.needs_widen(nd)} (expected {want})')


def t7():
    print('7. value head')
    torch.manual_seed(0)
    h = value_head.ValueHead(16, 32, 0.9)
    x = torch.randn(10, 16)
    with tempfile.TemporaryDirectory() as d:
        p = os.path.join(d, 'v.pt')
        value_head.save(p, h)
        h2 = value_head.load(p)
        ck(torch.allclose(torch.stack(h(x)), torch.stack(h2(x))), 'save/load round trip identical')
        v = h2.value(x)
        ck(all(0 <= a <= 1 for a in v), 'values in [0, 1]')
        # synthetic data: solvable iff feature 0 > 0, steps-to-go = 1 + 4 * |feature 1|
        N = 4000
        X = torch.randn(N, 16)
        n = torch.full((N,), 4.0)
        succ = (X[:, 0] > 0).float() * 4
        stg = succ * (1 + 4 * X[:, 1].abs())
        ti = torch.arange(N)
        held = torch.tensor([i % 10 == 0 for i in range(N)])
        torch.save(dict(feats=X.half(), n=n, succ=succ, stg=stg, depth=torch.zeros(N), ti=ti, heldout_thm=held),
                   os.path.join(d, 'data.pt'))
        import subprocess
        r = subprocess.run([sys.executable, os.path.join(ROOT, 'mcts_value_train.py'), '--data', os.path.join(d, 'data.pt'),
                            '--out', os.path.join(d, 'h.pt'), '--report', os.path.join(d, 'r.json'), '--epochs', '40',
                            '--batch', '256', '--hidden', '64'], capture_output=True, text=True)
        ck(r.returncode == 0, 'trainer runs' + ('' if r.returncode == 0 else r.stderr[-500:]))
        if r.returncode == 0:
            rep = json.load(open(os.path.join(d, 'r.json')))['heldout']
            ck(rep['auc_solvable'] > 0.95, f'held-out AUC {rep["auc_solvable"]}')
            ck(rep['stg_spearman'] > 0.8, f'held-out steps-to-go Spearman {rep["stg_spearman"]}')


if __name__ == '__main__':
    for t in (t1, t2, t3, t4, t5, t6, t7):
        t()
    print('FAILED' if FAIL else 'ALL OK', len(FAIL))
    sys.exit(1 if FAIL else 0)
