#!/usr/bin/env python3
"""Reviewer: Phase 0.1 (the known-proof estimator at small p), recounted from the reviewer's OWN capability-defs outputs
(~/review/capability-defs/review_cd/out_bracket.json, written by review_cd/rv_bracket.py in the capability-defs review):
per (seed, theorem) the known-proof sum LB = log sum_F pi_pend(y) at T 0.8 (exact 33-base terms where scored, else the
b0 - ln 33 bound) and the pooled pend sampling counts (c, n) over every standard-cap pend attempt (trajectory x0/x1,
mcts pool, J2, J9).  Ratio = exp(LB) / (c / n) for c >= 1, binned by p-hat; median and 10-90 % range per bin."""
import json, math, os, statistics, sys
B = json.load(open(os.path.expanduser('~/review/capability-defs/review_cd/out_bracket.json')))
bins = [('>=1e-3', 1e-3, 1), ('1e-4..1e-3', 1e-4, 1e-3), ('1e-5..1e-4', 1e-5, 1e-4), ('<1e-5', 0, 1e-5)]
rows = []
for s in ('0', '1', '2'):
    LB = B[s]['LB']; PS = B[s]['ps']
    for t, (c, n) in PS.items():
        if c < 1 or t not in LB or 'pend' not in LB[t]:
            continue
        lb = LB[t]['pend'][1]
        if lb is None or lb == -math.inf:
            continue
        rows.append((s, t, c, n, c / n, math.exp(lb) / (c / n)))
print(f'(seed, theorem) pairs with >= 1 pend success and a known-proof sum: {len(rows)}; per seed ' +
      str({s: sum(1 for r in rows if r[0] == s) for s in '012'}))
for nm, lo, hi in bins:
    rs = sorted(r[5] for r in rows if lo <= r[4] < hi)
    if not rs:
        print(f'{nm:12s} n 0'); continue
    q = lambda f: rs[min(len(rs) - 1, int(f * (len(rs) - 1) + 0.5))]
    print(f'{nm:12s} n {len(rs):4d}  median ratio {statistics.median(rs):.3f}  10-90 % [{q(0.1):.3f}, {q(0.9):.3f}]  '
          f'min p-hat {min(r[4] for r in rows if lo <= r[4] < hi):.2e}')
json.dump(rows, open(os.path.expanduser('~/review/create-or-elicit/review_coe/out_phase01.json'), 'w'))
