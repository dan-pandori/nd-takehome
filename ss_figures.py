#!/usr/bin/env python3
"""support-state figures: support-curves' per-theorem scatter (log p_base vs log p_EI, T 0.8, seed 0) for the SN
state models, next to the whole-proof one re-drawn from support-curves' own summary with the same code
(`sc_figures.scatter`, dataviz rules documented there).  Cells pool n and c over every file of this run with the
same (model, seed, T) -- stage 1 plus the H / S2 continuations, as support-curves pooled its stages.

  python3 ss_figures.py      # -> figures/ss_state_scatter.png, figures/ss_wholeproof_scatter.png
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ss_analysis as SA
from sc_figures import scatter

_, pooled = SA.load()
cells = []
for (model, seed, T), cs in pooled.items():
    for n, c in cs.items():
        cells.append({'name': n, 'model': model, 'seed': seed, 'temperature': T, 'L_true': SA.THM[n]['L_true'],
                      'n': c['n'], 'c': c['c'], 'p_hat': c['c'] / c['n']})
os.makedirs('figures', exist_ok=True)
scatter(cells, 'figures/ss_state', 0, 0.8)
scatter(SA.git_json('origin/dan_support-curves', 'artifacts/sc/summary.json'), 'figures/ss_wholeproof', 0, 0.8)
