#!/usr/bin/env python3
"""mcts_value_data.py -- rollouts of the frozen policy that label proof states for the value head (run `mcts-a`).

For each theorem, k attempts share one name base, so the attempts of one theorem that reach the same state reach the
same `mcts.state_key`.  Every distinct (theorem, state) gets the trunk feature the search will feed the head
(`mcts.Sampler`, computed in the same forward that samples the state's next action), and three counts:
  n     attempts that passed through it;
  succ  of those, attempts that ended in a proof Lean accepted (lean_gate.gate on the literal text);
  stg   sum over the successful ones of the actions they still took (steps-to-go; 0 is never stored -- a finished
        proof is not a state).
Theorems: `rl_targets.jsonl` and a sample of the generator pool (K12 train).  Never textbook72, holdout250 or a transfer
pool (asserted by name prefix).  A held-out tenth of the theorems (by a hash of the name) is marked for calibration.

  python mcts_value_data.py --ckpt X.pt --targets data/ladder/rl_targets.jsonl --gen K12.jsonl[.gz] --n_gen 1500 \
      --k 16 --out artifacts/mcts/vdata_s0_r8.pt
"""
import argparse, collections, gzip, hashlib, json, os, random, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import torch
import mcts
from state_env import Env

FORBIDDEN = ('textbook_', 'h250', 'holdout', 'lp_transfer', 'transfer', 'tb72')


def heldout(name):
    return int(hashlib.md5(name.encode()).hexdigest(), 16) % 10 == 0


def read(fn):
    op = gzip.open if fn.endswith('.gz') else open
    with op(fn, 'rt') as f:
        return [json.loads(l) for l in f]


def rollouts(model, tok, prompts, k, temp, max_steps, max_action, seed, log=print, chunk=256, lean=True):
    rng = random.Random(seed)
    S = mcts.Sampler(model, tok, max_action=max_action, temp=temp, seed=seed)
    sid = {}                     # (ti, key) -> state id
    feats, s_ti, s_depth = [], [], []
    att_ti, att_path, att_end, att_env = [], [], [], []
    ends = collections.Counter()
    t0 = time.time()
    for c0 in range(0, len(prompts), chunk):
        live = []
        for ti in range(c0, min(len(prompts), c0 + chunk)):
            b = rng.randint(0, mcts.NAME_BASE_MAX)
            e0 = Env(prompts[ti], canon=True, base=b, assign=True)
            for _ in range(k):
                a = len(att_ti)
                att_ti.append(ti); att_path.append([]); att_end.append(None); att_env.append(None)
                live.append((a, mcts.clone(e0)))
        while live:
            groups = collections.OrderedDict()
            for a, e in live:
                groups.setdefault((att_ti[a], mcts.state_key(e)), []).append((a, e))
            bycount = collections.defaultdict(list)
            for g, mem in groups.items():
                bycount[len(mem)].append(g)
            nxt = []
            for cnt, gs in bycount.items():
                pids = [tok.encode_toks(groups[g][0][1].state_tokens()) for g in gs]
                acts, fs = S(pids, cnt, want_feat=True)
                for g, A, f in zip(gs, acts, fs):
                    if g not in sid:
                        sid[g] = len(feats); feats.append(f.half().cpu()); s_ti.append(g[0])
                        s_depth.append(groups[g][0][1].steps)
                    s = sid[g]
                    for (a, e), (ids, lp, ended) in zip(groups[g], A):
                        att_path[a].append(s)
                        if not ended:
                            att_end[a] = 'truncated'; ends['truncated'] += 1; continue
                        atoks, _ = tok.decode_action(ids)
                        ok, why = e.apply(atoks)
                        if not ok:
                            att_end[a] = 'syntax'; ends['syntax'] += 1; continue
                        if e.done:
                            att_end[a] = 'done'; att_env[a] = e; ends['done'] += 1; continue
                        if e.steps >= max_steps:
                            att_end[a] = 'step_cap'; ends['step_cap'] += 1; continue
                        nxt.append((a, e))
            live = nxt
        log(f'theorems {min(len(prompts), c0 + chunk)}/{len(prompts)} states {len(feats)} wall {time.time() - t0:.0f}s '
            f'ends {dict(ends)}')
    # Lean decides the finished attempts
    fin = [a for a in range(len(att_ti)) if att_end[a] == 'done']
    texts = [tok.text(att_env[a].text) for a in fin]
    nds = [att_env[a].nd() for a in fin]
    pr = [prompts[att_ti[a]] for a in fin]
    tl = time.time()
    if lean:
        from lean_gate import gate
        res = gate(tok, pr, nds, texts)
    else:
        res = nds
    lean_s = time.time() - tl
    ok = [False] * len(att_ti)
    for a, r in zip(fin, res):
        ok[a] = not r.startswith('LEAN')
    n = torch.zeros(len(feats)); succ = torch.zeros(len(feats)); stg = torch.zeros(len(feats))
    for a in range(len(att_ti)):
        T = len(att_path[a])
        for j, s in enumerate(att_path[a]):
            n[s] += 1
            if ok[a]:
                succ[s] += 1; stg[s] += T - j
    stats = dict(ends=dict(ends), attempts=len(att_ti), accepted=sum(ok), lean_checks=len(fin), lean_s=lean_s,
                 wall_s=time.time() - t0, sampler_gpu_s=S.gpu_s, gen_tokens=S.gen_tokens, prompt_tokens=S.prompt_tokens,
                 states=len(feats))
    return dict(feats=torch.stack(feats), ti=torch.tensor(s_ti), depth=torch.tensor(s_depth), n=n, succ=succ, stg=stg,
                att_ok=torch.tensor(ok), att_ti=torch.tensor(att_ti)), stats


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--ckpt', required=True)
    ap.add_argument('--targets', default='data/ladder/rl_targets.jsonl')
    ap.add_argument('--gen', default=None)
    ap.add_argument('--n_gen', type=int, default=1500)
    ap.add_argument('--n_targets', type=int, default=0, help='0 = all')
    ap.add_argument('--k', type=int, default=16)
    ap.add_argument('--temp', type=float, default=1.0)
    ap.add_argument('--max_steps', type=int, default=96)
    ap.add_argument('--max_action', type=int, default=256)
    ap.add_argument('--seed', type=int, default=0)
    ap.add_argument('--out', required=True)
    ap.add_argument('--no_lean', action='store_true')
    a = ap.parse_args()
    from model import load_ckpt
    dev = 'cuda' if torch.cuda.is_available() else 'cpu'
    model, tok, _ = load_ckpt(a.ckpt, dev)
    rows = [dict(name=r['name'], prompt=r['prompt'], src='rl_targets') for r in read(a.targets)]
    if a.n_targets:
        rows = random.Random(a.seed).sample(rows, a.n_targets)
    if a.gen:
        g = read(a.gen)
        g = random.Random(a.seed + 1).sample(g, min(a.n_gen, len(g)))
        rows += [dict(name=r.get('name', f'k12_{i}'), prompt=r['prompt'], src='gen') for i, r in enumerate(g)]
    for r in rows:
        assert not any(r['name'].startswith(p) for p in FORBIDDEN), r['name']
    random.Random(a.seed + 2).shuffle(rows)
    data, st = rollouts(model, tok, [r['prompt'] for r in rows], a.k, a.temp, a.max_steps, a.max_action, a.seed,
                        lean=not a.no_lean)
    data['heldout_thm'] = torch.tensor([heldout(r['name']) for r in rows])
    data['names'] = [r['name'] for r in rows]
    data['src'] = [r['src'] for r in rows]
    st.update(ckpt=a.ckpt, k=a.k, temp=a.temp, n_theorems=len(rows))
    if dev == 'cuda':
        st['peak_alloc_gb'] = torch.cuda.max_memory_allocated() / 2 ** 30
    data['stats'] = st
    os.makedirs(os.path.dirname(a.out) or '.', exist_ok=True)
    torch.save(data, a.out)
    json.dump(st, open(a.out.replace('.pt', '.json'), 'w'), indent=1)
    print(json.dumps(st))


if __name__ == '__main__':
    main()
