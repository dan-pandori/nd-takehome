#!/usr/bin/env python3
"""lit-measures M2 amendment 1: 8 re-runs (r1-r8) of cell (init 0, data 100) with identical seeds, plus the grid's own
i0_d100 run: the spread that GPU non-determinism alone gives, next to the 64-cell grid's sd.
  python3 lm_m2_reps.py  -> artifacts/lit-measures/m2/reps.json (and prints)"""
import json, statistics
from lm_m2 import cell, INITS, DATAS
reps = {'grid': cell(0, 100), **{f'r{k}': cell(0, 100, f'r{k}') for k in range(1, 9)}}
grid = [cell(i, d) for i in INITS for d in DATAS]
out = {'cells': reps}
for q in ('depth3', 'overall', 'val_loss'):
    v = [r[q] for r in reps.values()]; g = [c[q] for c in grid]
    out[q] = {'rep_values': v, 'rep_sd': statistics.stdev(v), 'rep_range': [min(v), max(v)], 'grid_sd': statistics.stdev(g),
              'rep_var_over_grid_var': statistics.variance(v) / statistics.variance(g)}
    print(f"{q:9s} replicates (n={len(v)}) sd {statistics.stdev(v):.4f} range [{min(v):.4f}, {max(v):.4f}] | grid sd {statistics.stdev(g):.4f} | var ratio {out[q]['rep_var_over_grid_var']:.2f}")
print('depth-3 per replicate:', ' '.join(f"{k} {r['depth3']:.3f}" for k, r in reps.items()))
json.dump(out, open('artifacts/lit-measures/m2/reps.json', 'w'), indent=1)
