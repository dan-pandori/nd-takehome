#!/usr/bin/env python3
"""Reviewer recount part 2: falsifier at the pre-registered attempt budget, pass@k, Lean share."""
import json, glob, collections, os, math
from fractions import Fraction

rows = []
for f in sorted(glob.glob('artifacts/sc/s*.jsonl')):
    if 'secondary' in f: continue
    for l in open(f):
        if l.strip():
            r = json.loads(l); r['_file'] = os.path.basename(f); rows.append(r)
THMS = [json.loads(l) for l in open('data/sc/theorems.jsonl')]
NAMES = [t['name'] for t in THMS]; L = {t['name']: t['L_true'] for t in THMS}
by = collections.defaultdict(dict)     # (stage, model, seed, T) -> name -> rec
for r in rows:
    by[(r['stage'], r['model'], r['seed'], r['temperature'])][r['name']] = r

# --- ordered stage chains for base s0 per temperature (sampling is i.i.d., so attempts concatenate)
CHAIN = {0.8: [('s1', 10000), ('s2a_T08', 40000), ('s2c_T08', 150000)],
         1.0: [('s2a_T10', 10000), ('s2b_T10', 40000), ('s2c_T10', 150000)]}

def zero_within(name, T, budget):
    """True iff base s0 had 0 successes in the first `budget` attempts at temperature T.
       Returns None if fewer than `budget` attempts exist for this theorem."""
    left = budget
    for stage, kmax in CHAIN[T]:
        r = by[(stage, 'base', 0, T)].get(name)
        if r is None:
            return None if left > 0 else False
        take = min(left, r['n_tried'])
        if r['first_hit'] is not None and r['first_hit'] <= take:
            return False
        left -= take
        if left <= 0:
            return True
        if r['n_tried'] < kmax:          # stopped early with successes -> already caught above
            pass
    return None if left > 0 else True

phi = [l.strip() for l in open('data/sc/crux_forward_phi.txt') if l.strip()]
ei = by[('s1', 'ei', 0, 0.8)]
print('=== Falsifier count as a function of the base-attempt budget per temperature ===')
print('  (forward crux, p_hat_EI >= 0.01, 0 base successes at BOTH temperatures within the budget)')
for budget in (40000, 50000, 100000, 150000, 200000):
    ok = [n for n in phi if zero_within(n, 0.8, budget) and zero_within(n, 1.0, budget)]
    und = [n for n in phi if zero_within(n, 0.8, budget) is None or zero_within(n, 1.0, budget) is None]
    print(f'  budget {budget:7d}/temperature: survivors {len(ok):3d}   (undetermined: {len(und)})')

print()
print('=== E7: pass@k per L_true stratum, unbiased estimator on the pooled T=0.8 seed-0 draw ===')
def passk(n, c, k):
    """1 - C(n-c,k)/C(n,k), exact, for k<=n."""
    if k > n: return None
    if c == 0: return 0.0
    if n - c < k: return 1.0
    num = Fraction(1)
    for i in range(k):
        num *= Fraction(n - c - i, n - i)
    return float(1 - num)

strata = collections.defaultdict(list)
for n in NAMES: strata[L[n]].append(n)
KS = [32, 100, 320, 1000, 3200, 10000]
print(f"  {'L':>2s} {'m':>3s} " + ' '.join(f'{"b@"+str(k):>9s} {"e@"+str(k):>9s}' for k in KS))
for Lv in sorted(strata):
    ns = strata[Lv]
    line = f'  {Lv:2d} {len(ns):3d} '
    for k in KS:
        b = sum(passk(by[('s1','base',0,0.8)][n]['n_tried'], by[('s1','base',0,0.8)][n]['n_ok'], k) or 0 for n in ns)/len(ns)
        e = sum(passk(by[('s1','ei',0,0.8)][n]['n_tried'], by[('s1','ei',0,0.8)][n]['n_ok'], k) or 0 for n in ns)/len(ns)
        line += f'{b:9.4f} {e:9.4f} '
    print(line)
print('  NOTE: for theorems that stopped early, n < k for large k; pass@k there is the value at n (a lower bound on EI, and')
print('        EI is the model that stops early), so the EI columns at k >= 2048 are conservative.')

print()
print('=== E12: Lean share of sampler wall time ===')
for key in [('s1','base',0,0.8), ('s1','ei',0,0.8), ('s3','base',1,0.8), ('s3','ei',1,0.8),
            ('s2a_T08','base',0,0.8), ('s2c_T08','base',0,0.8), ('s2c_T10','base',0,1.0)]:
    d = by.get(key)
    if not d: continue
    g = sum(r['gen_s'] for r in d.values()); l = sum(r['lean_s'] for r in d.values()); w = sum(r['wall_s'] for r in d.values())
    n = sum(r['n_tried'] for r in d.values())
    print(f'  {str(key):34s} gen {g/w:5.1%}  lean {l/w:5.1%}  other {1-(g+l)/w:5.1%}   {n/w:6.0f} samp/s-per-job  ({len(d)} thms)')

print()
print('=== Distinct normalised strings per theorem (the reason Lean is cheap) ===')
for key in [('s1','base',0,0.8), ('s1','ei',0,0.8)]:
    d = by[key]; v = sorted(r['n_distinct_strings'] for r in d.values())
    print(f'  {str(key):22s} min {v[0]} median {v[len(v)//2]} max {v[-1]}  (k=10,000 each)')
