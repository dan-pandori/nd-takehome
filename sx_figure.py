#!/usr/bin/env python3
"""figures/search_expert.png from artifacts/sx/analysis.json (sx_analysis.py). Left: read-out Q per seed (no search).
Right: targets the expert solves in round r that the other arm's expert never solved in rounds <= r, summed over seeds."""
import json, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
d = json.load(open('artifacts/sx/analysis.json'))
C = {'A': '#2a78d6', 'B': '#eb6834', 'C': '#1baf7a', 'A2': '#eda100', 'T1': '#6b6a64'}
fig, (ax, bx) = plt.subplots(1, 2, figsize=(11, 4.2))
for s in range(6):
    qa, qb = d['reads'][f'A_s{s}']['Q'], d['reads'][f'B_s{s}']['Q']
    ax.plot([s - 0.12, s + 0.12], [qa, qb], color='#c3c2b7', lw=1.5, zorder=1)
lab = {'A': 'A sampling expert', 'B': 'B best-first expert', 'A2': 'A2 (A re-drawn)', 'C': 'C truncate-and-resume',
       'T1': 'state-cap12 T1 (all-successes rule; secondary)'}
off = {'A': -0.12, 'B': 0.12, 'A2': -0.3, 'C': 0.3, 'T1': 0.0}
mk = {'A': 'o', 'B': 's', 'A2': 'D', 'C': '^', 'T1': 'x'}
for arm in ('A', 'B', 'A2', 'C', 'T1'):
    xs = [s + off[arm] for s in range(6) if f'{arm}_s{s}' in d['reads']]
    ys = [d['reads'][f'{arm}_s{s}']['Q'] for s in range(6) if f'{arm}_s{s}' in d['reads']]
    ax.scatter(xs, ys, s=42, marker=mk[arm], color=C[arm], label=lab[arm], zorder=2, edgecolors='white' if mk[arm] != 'x' else None, linewidths=1)
ax.set_xticks(range(6)); ax.set_xticklabels([f'seed {s}' for s in range(6)])
ax.set_ylabel('theorems solved, k 256, no search (Q, of 291)')
ax.set_title('Apprentice read-out: B − A mean −1.3 (MDD 18)', fontsize=10)
ax.legend(fontsize=7.5, frameon=False, loc='upper left', ncol=2); ax.set_ylim(60, 275)
for sp in ('top', 'right'):
    ax.spines[sp].set_visible(False); bx.spines[sp].set_visible(False)
ax.grid(axis='y', color='#e6e5df', lw=0.8); ax.set_axisbelow(True)
R = d['rounds']
for x, y, ls in (('B', 'A', '-'), ('A', 'B', '-'), ('C', 'A2', '--'), ('A2', 'C', '--')):
    keys = [k for k in R if k.startswith(f'{x}_s') and k.endswith(f'_vs_{y}')]
    tot = [sum(R[k][r]['past_other'] for k in keys) / len(keys) for r in range(8)]
    bx.plot(range(1, 9), tot, ls, color=C[x], lw=2, marker=mk[x], ms=6, label=f'{x} (vs {y}), mean of {len(keys)} seeds')
bx.set_xlabel('EI round'); bx.set_ylabel("targets solved that the other expert never solved")
bx.set_title('Experts on the 4,495 training targets (B spends 23 % of A\'s actions)', fontsize=10)
bx.legend(fontsize=7.5, frameon=False); bx.grid(axis='y', color='#e6e5df', lw=0.8); bx.set_axisbelow(True)
bx.set_ylim(bottom=0)
fig.text(0.01, 0.01, 'SN-cap12 (lean_staten, 3.2 M params, from scratch, Stage-1 on K12) + 8 EI rounds; Lean alone decides; run search-expert', fontsize=7, color='#6b6a64')
fig.tight_layout(rect=(0, 0.03, 1, 1))
fig.savefig('figures/search_expert.png', dpi=150)
