#!/usr/bin/env python3
"""figures/frontier_supply.png: per-seed read-out solves, C vs S (and C′), SN-cap12 r8 checkpoints; from artifacts/fsup/summary.json."""
import json
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
d = json.load(open('artifacts/fsup/summary.json'))['readouts']['per_seed']
INK, MUTED, GRID = '#1f1f1e', '#6b6a64', '#e4e3dd'
ARM = {'C': ('control C', '#2a78d6', 'o'), 'S': ('supply S', '#eb6834', 's'), 'R': ("control rerun C′", '#8a8a85', 'D')}
fig, axes = plt.subplots(1, 2, figsize=(10, 4), facecolor='#fcfcfb')
for ax, (q, title) in zip(axes, [('primary', 'Primary: the 91 + rr600 L 15–16 (of 291)'), ('lp2_91', 'Long-pool-2, L ≥ 17 (of 91)')]):
    ax.set_facecolor('#fcfcfb')
    for s in range(6):
        c, sv = d.get(f'C_s{s}', {}).get(q), d.get(f'S_s{s}', {}).get(q)
        if c is not None and sv is not None:
            ax.plot([s, s], [c, sv], color=GRID, lw=2, zorder=1)
    for arm, (lab, col, mk) in ARM.items():
        xs = [s + (0.18 if arm == 'R' else 0) for s in range(6) if f'{arm}_s{s}' in d]
        ys = [d[f'{arm}_s{s}'][q] for s in range(6) if f'{arm}_s{s}' in d]
        ax.scatter(xs, ys, s=64, color=col, marker=mk, edgecolor='#fcfcfb', linewidth=2, label=lab, zorder=3)
    ax.set_xticks(range(6)); ax.set_xticklabels([f's{s}' for s in range(6)], color=MUTED)
    ax.tick_params(colors=MUTED); ax.grid(axis='y', color=GRID, lw=0.8); ax.set_axisbelow(True)
    for sp in ax.spines.values(): sp.set_visible(False)
    ax.set_title(title, color=INK, fontsize=11, loc='left'); ax.set_xlabel('Stage-1 seed', color=MUTED)
    ax.set_ylabel('theorems solved (≥ 1 of 256 Lean-accepted)', color=MUTED)
axes[0].legend(frameon=False, labelcolor=INK, loc='lower right')
fig.suptitle('frontier-supply: SN-cap12 after 8 EI rounds, per seed (S − C mean +7.5 primary, +5.5 on the 91; paired MDD ≈ 10.5)', color=INK, fontsize=10)
fig.tight_layout(); fig.savefig('figures/frontier_supply.png', dpi=150)
