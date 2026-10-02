#!/usr/bin/env python3
"""Reviewer: (1) what the 8 flip-control passes are; (2) Lean on EVERY counted proof at pend x0 and r8 x0 (all seeds)."""
import json, glob, os, random, sys, collections, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rlean
R = os.path.expanduser('~/review/trajectory-cap6'); E = f'{R}/artifacts/tj6/eval'
rd = lambda fn: [json.loads(l) for l in open(fn) if l.strip()]
rng = random.Random(20261002)
pool = []
for fn in sorted(glob.glob(f'{E}/s0_r8__*_x0.jsonl')):
    for r in rd(fn):
        for p in r['proofs']: pool.append((r['prompt'], p, os.path.basename(fn), r['name']))
# replicate recheck.py's draw order exactly: unt, rej, flip
_ = rng.sample(pool, 60)
REJ = []
for fn in sorted(glob.glob(f'{E}/s?_*__*_x?.jsonl')):
    for r in rd(fn):
        fe = r.get('fail_example') or ''
        if fe.startswith('LEANREJ '): REJ.append(fe)
flipc = [x for x in pool if 'ORI' in x[1]]
fl = rlean.check([(p, rlean.render(p, b, flip=('Or.inl', 'Or.inr'))) for p, b, _, _ in flipc[:400]])
passed = [x for x, (o, _, _) in zip(flipc[:400], fl) if o]
import re
def ori_disj(x):
    out = []
    for part in x[1].split(' ; '):
        if ' : ORI' in part: out.append(part.split(' : ')[0].split(None, 1)[1].strip(' |'))
    return out
print(f'flip control on first 400 ORI proofs: {len(passed)} pass')
for x in passed[:12]: print('  ', ori_disj(x))
res = {'flip400_pass': len(passed), 'flip_pass_disj': [ori_disj(x) for x in passed]}
t0 = time.time(); res['all'] = {}
for s in (0, 1, 2):
    for ck in ('pend', 'r8'):
        items = []
        for pool_ in ('tb72', 'h250'):
            for r in rd(f'{E}/s{s}_{ck}__{pool_}_x0.jsonl'):
                for p in r['proofs']: items.append((r['prompt'], p, r['name']))
        rr = rlean.check([(p, rlean.render(p, b)) for p, b, _ in items], per_file=300)
        fails = [(n, i) for (p, b, n), (o, i, _) in zip(items, rr) if not o]
        res['all'][f's{s}_{ck}'] = dict(n=len(items), ok=len(items) - len(fails), fails=fails[:10])
        print(f's{s} {ck}: {len(items) - len(fails)}/{len(items)} Lean-accepted  {time.time()-t0:.0f}s', flush=True)
json.dump(res, open(f'{R}/rv6/recheck_all.json', 'w'), indent=0)
