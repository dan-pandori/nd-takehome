#!/usr/bin/env python3
"""lit-measures M2 default-reproduction check (preregistration §M2).  Reads artifacts/lit-measures/m2/repro/:
  {new,newx,orig}_{legacy,fast}.jsonl  300 steps, --seed 0, logged every 10 steps: new = this branch's train.py with the
      default data_seed, newx = explicit --data_seed 0, orig = origin/dan's train.py/fast_train.py (before the change);
  full_legacy_p1_s0.log  this branch, legacy, --seed 0 (default data_seed), 6,000 steps on data/nf/train_p1.jsonl, vs
  nf_stage1_p1_s0.log    noise-floor's own log of the same command (other pod / GPU).
Prints max |difference| of the logged train loss and val loss per pair."""
import json, re
D = 'artifacts/lit-measures/m2/repro/'
def met(fn):
    return {r['step']: (r['loss'], r.get('val2k')) for r in map(json.loads, open(D + fn)) if r.get('kind', 'step') == 'step' and 'loss' in r}
def log(fn):
    return {int(m[1]): (float(m[2]), float(m[3])) for m in re.finditer(r'^step (\d+) loss ([\d.]+) lr \S+ \S+ val ([\d.]+)', open(D + fn).read(), re.M)}
def cmp(a, b, name):
    ks = sorted(set(a) & set(b)); dl = max(abs(a[k][0] - b[k][0]) for k in ks); dv = max(abs(a[k][1] - b[k][1]) for k in ks if a[k][1] is not None)
    print(f'{name:40s} steps {len(ks):3d} ({ks[0]}..{ks[-1]})  max|dloss| {dl:.2e}  max|dval| {dv:.2e}  identical {dl == 0 and dv == 0}')
for impl in ('legacy', 'fast'):
    n, x, o = met(f'new_{impl}.jsonl'), met(f'newx_{impl}.jsonl'), met(f'orig_{impl}.jsonl')
    cmp(n, o, f'{impl}: default vs origin/dan'); cmp(n, x, f'{impl}: default vs --data_seed 0')
cmp(log('full_legacy_p1_s0.log'), log('nf_stage1_p1_s0.log'), 'legacy 6000: this branch vs noise-floor')
