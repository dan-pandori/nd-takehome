#!/usr/bin/env python3
"""Self-test of `state_search` (run search-expert), CPU or GPU:
  1. step-filter soundness: sample attempts WITHOUT the filter, run it in shadow mode, and check that no attempt the
     filter would have stopped is Lean-accepted (and count Lean rejects it misses);
  2. clone independence: a clone's apply never changes the original's state;
  3. search_generate / resume_generate run end to end within their budgets, and every proof they report is judged
     by Lean from its literal text.
  python3 se_selftest.py --ckpt ckpts/sc12/stage1_SN12_s0.pt --n 24 --k 8 [--device cpu]
"""
import argparse, collections, json, os, random, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import torch
from model import load_ckpt
from state_sample import env_generate
from state_search import StepFilter, clone, search_generate, resume_generate, _root
from eval_set import judge


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--ckpt', required=True); ap.add_argument('--device', default='cuda' if torch.cuda.is_available() else 'cpu')
    ap.add_argument('--targets', default='data/ladder/rl_targets.jsonl')
    ap.add_argument('--n', type=int, default=24); ap.add_argument('--k', type=int, default=8)
    ap.add_argument('--batch', type=int, default=256); ap.add_argument('--out', default='artifacts/se/selftest.json')
    a = ap.parse_args()
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    model, tok, _ = load_ckpt(a.ckpt, a.device)
    recs = [json.loads(l) for l in open(a.targets)]
    rng = random.Random(0)
    tg = rng.sample([r for r in recs if r['n_lines'] >= 9], a.n)
    res = {}
    # 1. shadow filter
    sf = StepFilter(tok)
    shadow = {}

    def shadow_filter(e):
        why = sf(e)
        if why and id(e) not in shadow:
            shadow[id(e)] = why
        return None
    prompts = [t['prompt'] for t in tg for _ in range(a.k)]
    envs = {}
    import state_sample
    orig_finish_env = state_sample.Env

    class RecEnv(orig_finish_env):
        def __init__(self, *x, **kw):
            super().__init__(*x, **kw); envs[len(envs)] = self
    state_sample.Env = RecEnv
    t0 = time.time()
    flat = env_generate(model, tok, prompts, greedy=False, temperature=0.8, batch=a.batch, seed=1, step_filter=shadow_filter)
    state_sample.Env = orig_finish_env
    ok = [not p.startswith(('LEANREJ', 'LEANPARSE')) for p in flat]
    rej = [p.startswith('LEANREJ') for p in flat]
    sh = [id(envs[i]) in shadow for i in range(len(prompts))]
    res['shadow'] = {'attempts': len(prompts), 'lean_ok': sum(ok), 'lean_rej': sum(rej),
                     'filter_would_stop': sum(sh), 'UNSOUND_filter_stop_but_lean_ok': sum(1 for o, s in zip(ok, sh) if o and s),
                     'lean_rej_filter_missed': sum(1 for r, s in zip(rej, sh) if r and not s),
                     'filter_reasons': dict(sf.rej), 'secs': time.time() - t0}
    print(res['shadow'], flush=True)
    # 2. clone independence
    e = _root(tg[0]['prompt'], tok, 5)
    before = (list(e.text), e.state_tokens(), e.steps)
    c = clone(e)
    c.apply(['have', 'n1', ':', 'P', ':=', 'h1', ';'])
    res['clone_independent'] = (list(e.text), e.state_tokens(), e.steps) == before
    print('clone independent', res['clone_independent'], flush=True)
    # 3. search / resume with the sampling arm's per-theorem actions as budgets
    acts = [0] * len(prompts)
    flat = env_generate(model, tok, prompts, greedy=False, temperature=0.8, batch=a.batch, seed=2, step_filter=StepFilter(tok), acts=acts)
    budgets = [sum(acts[i * a.k:(i + 1) * a.k]) for i in range(a.n)]
    rows = judge(tg, [flat[i * a.k:(i + 1) * a.k] for i in range(a.n)], 'n_lines')
    res['sample'] = {'solved': sum(1 for r in rows if r['n_ok']), 'actions': sum(budgets)}
    for name, fn, kw in (('search', search_generate, {'width': 4}), ('resume', resume_generate, {'chains': a.k})):
        st = {}
        t0 = time.time()
        out, info = fn(model, tok, [t['prompt'] for t in tg], budgets, temperature=0.8, batch=a.batch, seed=3, stats=st,
                       step_filter=StepFilter(tok), **kw)
        rows = judge(tg, [[p] for p in out], 'n_lines')
        over = sum(1 for x, b in zip(info, budgets) if x['actions'] > b)
        res[name] = {'solved': sum(1 for r in rows if r['n_ok']), 'actions': sum(x['actions'] for x in info), 'over_budget': over,
                     'lean_rej': sum(p.startswith('LEANREJ') for p in out), 'env_end': dict(st.get('env_end', {})), 'secs': time.time() - t0}
        print(name, res[name], flush=True)
    json.dump(res, open(a.out, 'w'), indent=1)


if __name__ == '__main__':
    main()
