#!/usr/bin/env python3
"""capability-defs: teacher-forced log p of fixed target proofs under a list of checkpoints, in the state environment.
A copy of run trajectory's `tj_score.py` (blob 570d558f on dan_trajectory) with one change: `--nbases N` scores only
the sampler's name bases 0..N-1 (default 33 = tj_score exactly).  With N < 33 the reported totals are
logsumexp_{b<N} cum_b - ln N, i.e. the base-marginalised log p *restricted to those bases*; since
pi(y) = (1/33) sum_{b<33} pi(y | b) >= (N/33) * [that restricted average], a valid lower bound on log pi(y) is
total + ln(N/33).  Used for J1 stage 1 (N = 1, every known proof) before exact 33-base rescoring of the top proofs.

  python3 cd_score.py --targets T.jsonl --ckpts ckpts.txt --out OUT [--nbases 1] [--lean]

`--targets`: jsonl, one target per line: {"tid", "name", "prompt", "kind", "proof"} (ND body).  `--ckpts`: a file of
`label path` lines.  Writes `<out>/targets.jsonl` (per target: actions, step kinds, replay status, Lean verdict and term
size with --lean) and `<out>/<label>.jsonl` (per target: per-step log p at T 1.0 and T 0.8 and the summaries).

Definition (preregistration/trajectory.md; after lit-measures' lm_m1.py):
  * the proof -> `state_env.decompose(prompt, proof, canon=True)` -> actions at base 0; replayed for every name base
    b = 0..32 in `Env(canon=True, assign=True, base=b)`, the sampler's environment.  Every action must apply, the
    environment must rename nothing and `inverse(env.text)` must give back the ND proof; otherwise the target is
    reported as a replay failure and not scored.
  * prompt = `tok.encode_toks(env.state_tokens())`, target = action tokens + <eos>; log p from one causal forward pass
    over prompt + target, natural logs, `log_softmax(logits / T)`.
  * the names an action DEFINES (`have n<k>`, and the binder of a box opener) are not scored: with assign=True the
    environment overwrites whatever the model writes there, so they are not the model's choice (at the first `have` the
    model can only guess the name base, ln 65 ~ 4.17 nats, which otherwise dominates every short proof's worst step).
    The tokens after them are conditioned on the canonical names, as the environment renders them.  The total with
    those tokens included is kept as `incl_names_total`.
  * the sampler draws b ~ U{0..32}: L(t) = logsumexp_b cum_b(t) - ln 33 (bases whose names would exceed MAXN have
    probability 0), step t contributes L(t) - L(t-1), L(0) = 0.  Contributions sum to log p(proof).
"""
import argparse, json, math, os, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import torch
import torch.nn.functional as F
from model import load_ckpt
from state_env import Env, decompose, is_name, parse_ftoks
from lean_tok import MAXN, ParseFail, inverse

NB = 33                 # the sampler's bases 0..32 (state_sample.NAME_BASE_MAX = 32); --nbases may lower it
TEMPS = (1.0, 0.8)
TOK_BUDGET = 1 << 18    # padded tokens per forward batch
FP16 = os.environ.get('TJ_BF16') == '1'    # default fp32: batched and direct sums then agree to 4 decimals (bf16: up to 0.2 nats)


def shift(toks, b):
    return [f'n{int(t[1:]) + b}' if is_name(t) else t for t in toks]


def step_kind(x):
    if x[0] == 'exact':
        return 'exact'
    h = x[x.index(':=') + 1]
    if h == '(':
        return 'box:neg' if parse_ftoks(x, 3)[0][0] == 'not' else 'box:imp'
    if h == 'Or.elim':
        return 'box:orelim'
    if h.startswith('h'):
        return 'prem'
    return h if not is_name(h) else 'name'


def defining(act):
    """positions (in the action's token list) of the names the environment assigns (state_env.Env._assign_names)."""
    if act[0] == 'exact':
        return ()
    j = act.index(':=')
    return (1, j + 4) if act[j + 1] == '(' else (1, j + 6) if act[j + 1] == 'Or.elim' else (1,)


def replay(prompt, proof):
    """-> (actions at base 0, max name index) or raise."""
    steps, toks, _ = decompose(prompt, proof, canon=True)
    acts = [a for _, a, _ in steps]
    mx = max((int(t[1:]) for t in toks if is_name(t)), default=0)
    return acts, mx


def states_at(prompt, proof, acts, b):
    env = Env(prompt, canon=True, base=b, assign=True)
    sts = []
    for a in acts:
        sts.append(env.state_tokens())
        ok, why = env.apply(shift(a, b))
        if not ok:
            raise ParseFail(f'replay b={b}: {why}')
    if not env.done:
        raise ParseFail(f'replay b={b}: not closed')
    if env.renamed:
        raise ParseFail(f'replay b={b}: env renamed {env.renamed}')
    if inverse(env.text) != proof:
        raise ParseFail(f'replay b={b}: ND mismatch')
    return sts


def build(targets, tok):
    """-> (meta rows, plan, seqs): plan[i] = list over bases of list over steps of a sequence key."""
    seqs, plan, meta = {}, {}, []
    for t in targets:
        m = {k: t[k] for k in ('tid', 'name', 'kind')}
        try:
            acts, mx = replay(t['prompt'], t['proof'])
            bases = [b for b in range(NB) if mx + b <= MAXN]
            per_b = []
            for b in bases:
                ks = []
                for st, act in zip(states_at(t['prompt'], t['proof'], acts, b), acts):
                    pid = tuple(tok.encode_toks(st)); qid = tuple(tok.encode_toks(shift(act, b)) + [tok.eos])
                    key = (pid, qid, defining(act))
                    seqs.setdefault(key, None); ks.append(key)
                per_b.append(ks)
        except (ParseFail, ValueError, KeyError, IndexError, AssertionError) as e:
            m.update(replay_ok=False, why=str(e)[:200]); meta.append(m); continue
        plan[t['tid']] = per_b
        m.update(replay_ok=True, n_steps=len(acts), n_bases=len(bases), max_name_b0=mx,
                 actions_b0=[' '.join(a) for a in acts], step_kind=[step_kind(a) for a in acts])
        meta.append(m)
    return meta, plan, list(seqs)


@torch.no_grad()
def score_seqs(model, keys, dev):
    """-> {key: {T: sum log p of the scored target tokens, ('incl', T): sum over all target tokens}}"""
    order = sorted(range(len(keys)), key=lambda i: len(keys[i][0]) + len(keys[i][1]))
    out = {}
    i = 0
    while i < len(order):
        L = len(keys[order[i]][0]) + len(keys[order[i]][1])
        j = i
        while j < len(order) and (j - i + 1) * (len(keys[order[j]][0]) + len(keys[order[j]][1])) <= TOK_BUDGET:
            j += 1
        j = max(j, i + 1)
        ch = [keys[order[q]] for q in range(i, j)]
        L = max(len(p) + len(q) for p, q, _ in ch)
        x = torch.zeros((len(ch), L), dtype=torch.long)
        for r, (p, q, _) in enumerate(ch):
            x[r, :len(p) + len(q)] = torch.tensor(p + q)
        x = x.to(dev)
        with torch.autocast('cuda', dtype=torch.bfloat16, enabled=FP16):
            logits = model(x[:, :-1])
        logits = logits.float()
        tgt = x[:, 1:, None]
        for T in TEMPS:
            lp = F.log_softmax(logits / T, -1).gather(-1, tgt).squeeze(-1).double().cpu()
            for r, (p, q, dm) in enumerate(ch):
                v = lp[r, len(p) - 1:len(p) + len(q) - 1]
                o = out.setdefault((p, q, dm), {})
                o[('incl', T)] = float(v.sum())
                o[T] = float(v.sum()) - sum(float(v[d]) for d in dm)
        i = j
    return out


def summarise(c, kinds):
    tot = sum(c)
    o = sorted(range(len(c)), key=lambda k: c[k])
    w1 = c[o[0]]; w2 = c[o[1]] if len(c) > 1 else 0.0
    return {'total': tot, 'mean': tot / len(c), 'w1': w1, 'w1_idx': o[0], 'w1_kind': kinds[o[0]], 'w2': w2,
            'rest_mean': (tot - w1) / (len(c) - 1) if len(c) > 1 else 0.0}


def per_target(res, per_b, T):
    M = torch.tensor([[res[k][T] for k in ks] for ks in per_b], dtype=torch.float64)    # [base, step]
    Mi = torch.tensor([[res[k][('incl', T)] for k in ks] for ks in per_b], dtype=torch.float64)
    incl = float(torch.logsumexp(Mi.sum(1), 0) - math.log(NB))
    Lc = torch.logsumexp(M.cumsum(1), 0) - math.log(NB)
    c = torch.diff(Lc, prepend=torch.zeros(1, dtype=Lc.dtype)).tolist()
    assert abs(sum(c) - float(Lc[-1])) < 1e-6
    return c, M[0].tolist(), incl


@torch.no_grad()
def direct_sum(model, per_b, dev):
    """independent check of base 0: each (state, action) alone, unpadded, T 1.0, all target tokens."""
    s = 0.0
    for p, q, _ in per_b[0]:
        x = torch.tensor([list(p) + list(q)], device=dev)
        with torch.autocast('cuda', dtype=torch.bfloat16, enabled=FP16):
            lg = model(x[:, :-1])
        lp = F.log_softmax(lg.float(), -1)[0, len(p) - 1:len(p) + len(q) - 1].gather(-1, x[0, len(p):, None]).sum()
        s += float(lp)
    return s


def lean_terms(targets, workers):
    import nd2lean
    from lean_check import check
    srcs, idx = [], []
    for i, t in enumerate(targets):
        try:
            srcs.append(nd2lean.translate(t['prompt'], t['proof'], require_all_pr=False)); idx.append(i)
        except Exception:
            pass
    res, _, _ = check(srcs, workers=workers)
    out = {t['tid']: {'lean_ok': False, 'term_size': None, 'lean_why': 'translate failed'} for t in targets}
    for i, r in zip(idx, res):
        out[targets[i]['tid']] = {'lean_ok': bool(r['ok']), 'term_size': r.get('size'), 'lean_why': None if r['ok'] else str(r.get('reason', ''))[:200]}
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--targets', required=True)
    ap.add_argument('--ckpts', required=True, help='file of "label path" lines')
    ap.add_argument('--out', required=True)
    ap.add_argument('--lean', action='store_true', help='Lean-check every target (lean_check) and record its term size')
    ap.add_argument('--workers', type=int, default=32)
    ap.add_argument('--nbases', type=int, default=33, help='score name bases 0..N-1 only (lower bound: total + ln(N/33))')
    a = ap.parse_args()
    global NB
    assert 1 <= a.nbases <= 33
    NB = a.nbases
    os.makedirs(a.out, exist_ok=True)
    import record    # results registry: job-level compute row (GPU-seconds) for this scoring job
    record.save_config(vars(a), os.path.join(a.out, 'run'), arm=os.environ.get('ND_ARM', 'j1_score'))
    dev = 'cuda' if torch.cuda.is_available() else 'cpu'
    targets = [json.loads(l) for l in open(a.targets) if l.strip()]
    assert len({t['tid'] for t in targets}) == len(targets)
    cks = [l.split() for l in open(a.ckpts) if l.strip()]
    _, tok, _ = load_ckpt(cks[0][1], 'cpu')
    assert tok.mode == 'lean_staten' and tok.canon and not tok.with_history
    t0 = time.time()
    meta, plan, keys = build(targets, tok)
    print(f'targets {len(targets)}: replay ok {len(plan)}, failed {len(targets) - len(plan)}; {len(keys)} distinct '
          f'(state, action) sequences; {time.time() - t0:.0f}s', flush=True)
    if a.lean:
        lt = lean_terms(targets, a.workers)
        for m in meta:
            m.update(lt[m['tid']])
        print(f"lean: {sum(m['lean_ok'] for m in meta)}/{len(meta)} accepted", flush=True)
    with open(os.path.join(a.out, 'targets.jsonl'), 'w') as f:
        for m in meta:
            f.write(json.dumps(m) + '\n')
    kinds = {m['tid']: m.get('step_kind') for m in meta}
    for label, path in cks:
        op = os.path.join(a.out, f'{label}.jsonl')
        if os.path.exists(op):
            print(f'skip {label}', flush=True); continue
        t1 = time.time()
        model, _, extra = load_ckpt(path, dev)
        res = score_seqs(model, keys, dev)
        with open(op + '.tmp', 'w') as f:
            for tid, per_b in plan.items():
                o = {'tid': tid, 'ckpt': label}
                for T in TEMPS:
                    c, raw, incl = per_target(res, per_b, T)
                    s = summarise(c, kinds[tid])
                    s['step_lp'] = [round(v, 4) for v in c]
                    s['raw_b0_total'] = sum(raw)
                    s['incl_names_total'] = incl
                    o[f'T{T}'] = s
                f.write(json.dumps(o) + '\n')
        os.replace(op + '.tmp', op)
        for tid in list(plan)[:3]:
            d = direct_sum(model, plan[tid], dev); b = sum(res[k][('incl', 1.0)] for k in plan[tid][0])
            print(f'  sanity {tid}: batched {b:.4f} direct {d:.4f} |diff| {abs(b - d):.4f}', flush=True)
        print(f'{label}: {len(plan)} targets, {time.time() - t1:.1f}s', flush=True)
        del model
        if dev == 'cuda':
            torch.cuda.empty_cache()


if __name__ == '__main__':
    main()
