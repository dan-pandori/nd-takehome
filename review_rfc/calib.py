#!/usr/bin/env python3
"""Reviewer: x_ctrl form with the null fitted on the end arm measured the same way (end-arm r8 x1 vs x under the
end arm's own replay control r8), then the excess at the four early starts; plus how much replay moves x."""
import json, os, numpy as np, sys
sys.argv = ['x']; exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'analysis.py')).read().split("PRE = (5.34, 0.482)")[0])
X, Y = [], []
for s in (0, 1, 2):
    ys = y(s, 'pend'); X += [xc[s, 'pend'][n] for n in NAMES]; Y += [n in ys for n in NAMES]
bc = fit(X, Y); print(f'calibrated null (end arm vs its control x): b0 {bc[0]:.3f} b1 {bc[1]:.3f} x50 {-bc[0]/bc[1]:.2f}')
for thr in (-12, -16):
    tot = []
    for st in STARTS + ['pend']:
        row = []
        for s in (0, 1, 2):
            ys = y(s, st); low = [n for n in NAMES if xc[s, st][n] < thr]
            row.append(sum(n in ys for n in low) - float(P(bc[0], bc[1], [xc[s, st][n] for n in low]).sum()))
        if st != 'pend': tot.append(row)
        print(f'  thr {thr} {st}: excess per seed {[round(v,1) for v in row]}')
    print(f'  thr {thr}: early-start total {np.sum(tot):.1f}; per seed {[round(v,1) for v in np.sum(tot,0)]}')
print('\nmedian (x_ctrl - x_start) over the 315 refs, per start and seed (replay shift of the worst step):')
for st in STARTS + ['pend']:
    print(st, [round(float(np.median([xc[s, st][n] - xs[s, st][n] for n in NAMES])), 2) for s in (0, 1, 2)],
          'median x_start', [round(float(np.median([xs[s, st][n] for n in NAMES])), 2) for s in (0, 1, 2)])
