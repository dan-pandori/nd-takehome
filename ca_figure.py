#!/usr/bin/env python3
"""figures/ca_depth3.png: depth-3 slice (half B, 250 theorems) per seed, E24 endpoint vs one variant,
over the grey min-max range of the run's own trajectory checkpoints.  Reads artifacts/ca/summary.json
and the per-theorem half-B files.   python3 ca_figure.py [variant]   (default: LSd3)"""
import gzip, json, sys
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from ca_plan import candidates

V = sys.argv[1] if len(sys.argv) > 1 else 'LSd3'
S = json.load(open('artifacts/ca/summary.json'))
INK, INK2, SURF, C1, C2 = '#0b0b0b', '#52514e', '#fcfcfb', '#2a78d6', '#eb6834'


def d3(stem):
    rows = [json.loads(l) for l in gzip.open(f'artifacts/ca/ev/{stem}.jsonl.gz', 'rt')]
    g = [r['lean_ok'] for r in rows if r['depth3']]
    return sum(g) / len(g)


fig, axes = plt.subplots(1, 2, figsize=(9, 4.0), gridspec_kw={'width_ratios': [8, 4]}, facecolor=SURF)
for ax, arm in zip(axes, ('W', 'F')):
    A = S['arms'][arm]; seeds = A['seeds']
    for i, r in enumerate(seeds):
        tr = [d3(c) for c in candidates(r) if '.step' in c]
        ax.plot([i, i], [min(tr), max(tr)], color='#d6d5cf', lw=8, solid_capstyle='round', zorder=1)
    e = A['variants']['E24']['per_seed']['depth3']; v = A['variants'][V]['per_seed']['depth3']
    x = range(len(seeds))
    ax.scatter([i - 0.12 for i in x], e, s=46, marker='o', color=C1, edgecolor=SURF, linewidth=1.5, zorder=3,
               label=f'E24 endpoint (sd {A["variants"]["E24"]["sd"]["depth3"]:.2f})')
    ax.scatter([i + 0.12 for i in x], v, s=46, marker='s', color=C2, edgecolor=SURF, linewidth=1.5, zorder=3,
               label=f'{V} (sd {A["variants"][V]["sd"]["depth3"]:.2f})')
    ax.axhline(S['cut'], color=INK2, lw=0.8, ls=(0, (3, 3)), zorder=0)
    ax.set_xticks(list(x)); ax.set_xticklabels([str(i) for i in x], color=INK2)
    ax.set_xlabel('seed', color=INK2); ax.set_ylim(-0.02, 1.02); ax.set_facecolor(SURF)
    ax.set_title(f'arm {arm}', color=INK, fontsize=10, loc='left', pad=26)
    for sp in ('top', 'right'):
        ax.spines[sp].set_visible(False)
    for sp in ('left', 'bottom'):
        ax.spines[sp].set_color('#b5b4ad')
    ax.tick_params(colors=INK2)
    ax.legend(frameon=False, fontsize=8, loc='lower left', bbox_to_anchor=(0, 1.06), ncol=2, labelcolor=INK)
axes[0].set_ylabel('depth-3 greedy solve rate (half B)', color=INK2)
axes[0].text(-0.45, S['cut'] + 0.015, 'cut 0.44', color=INK2, fontsize=7, ha='left')
fig.suptitle('Depth-3 slice per seed: decayed 24k endpoint vs %s; grey = range over the run\'s trajectory checkpoints' % V,
             fontsize=9, color=INK)
fig.text(0.01, 0.005, '3,214,336-param from-scratch lean_seq cap-6 GPTs (stage1-dynamics arms W, F); Lean-alone judge; 250 depth-3 theorems',
         fontsize=6.5, color=INK2)
fig.tight_layout(rect=(0, 0.03, 1, 0.95))
fig.savefig('figures/ca_depth3.png', dpi=150, facecolor=SURF)
print('figures/ca_depth3.png', V)
