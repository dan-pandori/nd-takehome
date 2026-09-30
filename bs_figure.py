#!/usr/bin/env python3
"""Figure for run_best_state.md: textbook72 (pass@256, /72) and Robbie's dev metric (dev 1,108, k 64, >= 7) by cell,
frozen and T1; bar = IQM, dots = seeds.  Reads artifacts/bs/summary.json (bs_analysis.py).

  python3 bs_figure.py   -> figures/best_state.png
"""
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

S = json.load(open('artifacts/bs/summary.json'))['cells']
CELLS = [('ours-cap6', 'ours\ncap 6 (3.2M)'), ('best-cap6', 'best\ncap 6 (9.6M)'),
         ('ours-cap12', 'ours\ncap 12 (3.2M)'), ('best-cap12', 'best\ncap 12 (9.6M)')]
STAGES = [('Fz', 'frozen (Stage-1)', '#2a78d6'), ('T1', 'T1 (8 ladder rounds)', '#eb6834')]
INK, MUTED, GRID = '#1f1f1e', '#6b6a64', '#e6e5e0'

fig, axes = plt.subplots(1, 2, figsize=(11, 4.2), facecolor='#fcfcfb')
for ax, (q, title, top) in zip(axes, (('tb72', 'textbook72 solved (of 72), pass@256', 72),
                                       ('dev', "Robbie's dev metric (of 1,108), k 64", 1108))):
    ax.set_facecolor('#fcfcfb')
    for i, (c, _) in enumerate(CELLS):
        for j, (st, lab, col) in enumerate(STAGES):
            d = S.get(c, {}).get(st, {}).get(q)
            if not d:
                continue
            x = i + (j - 0.5) * 0.36
            ax.bar(x, d['iqm'], width=0.32, color=col, alpha=0.85, label=lab if i == 0 else None, zorder=2)
            seeds = [v for v in d['per_seed'] if v is not None]
            ax.scatter([x + (k - (len(seeds) - 1) / 2) * 0.05 for k in range(len(seeds))], seeds, s=16, color=INK,
                       zorder=3, edgecolor='#fcfcfb', linewidth=0.8)
            ax.text(x, top * 0.015, f"{d['iqm']:.0f}", ha='center', va='bottom', fontsize=8, color='#ffffff', fontweight='bold', zorder=4)
    ax.set_xticks(range(len(CELLS)), [l for _, l in CELLS], fontsize=8.5, color=INK)
    ax.set_title(title, fontsize=10, color=INK, loc='left')
    ax.grid(axis='y', color=GRID, zorder=0)
    for s in ('top', 'right'):
        ax.spines[s].set_visible(False)
    for s in ('left', 'bottom'):
        ax.spines[s].set_color(MUTED)
    ax.tick_params(colors=MUTED, labelsize=8)
axes[0].legend(frameon=False, fontsize=8, loc='upper left')
fig.text(0.01, 0.01, 'Bar = IQM over seeds (3 new; 2 / 4 inherited), dots = seeds. Lean alone decides. '
         'State format (lean_staten), proof-state environment.', fontsize=7.5, color=MUTED)
fig.tight_layout(rect=(0, 0.04, 1, 1))
import os
os.makedirs('figures', exist_ok=True)
fig.savefig('figures/best_state.png', dpi=150)
print('figures/best_state.png')
