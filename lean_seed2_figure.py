#!/usr/bin/env python3
"""Figure for run lean-seed2, from artifacts/ls2/summary.json (lean_seed2_analysis.py) -> figures/lean_seed2.png.
Categorical colours = dataviz reference palette slots 1-3 in fixed order (token blue, Stage-1 seed 0 orange, Stage-1 seed 2 aqua;
the first three slots validate all-pairs); identity never colour-alone: legend + direct labels, frozen controls dashed."""
import json, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

S = json.load(open('artifacts/ls2/summary.json'))
P3 = S['E2_E5_ladder']
COL = {'token': '#2a78d6', 'seed0': '#eb6834', 'seed2': '#1baf7a'}
NAME = {'token': 'token format (abs), Stage-1 seed 0', 'seed0': 'lean_seq, Stage-1 seed 0 (lean-format run)', 'seed2': 'lean_seq, Stage-1 seed 2 (this run)'}
INK, MUTED, SURF = '#0b0b0b', '#52514e', '#fcfcfb'
plt.rcParams.update({'font.size': 8.5, 'axes.edgecolor': '#c9c8c2', 'axes.labelcolor': MUTED, 'xtick.color': MUTED, 'ytick.color': MUTED, 'text.color': INK,
                     'axes.spines.top': False, 'axes.spines.right': False, 'figure.facecolor': SURF, 'axes.facecolor': SURF, 'savefig.facecolor': SURF})
fig, ax = plt.subplots(1, 2, figsize=(10.5, 3.9), gridspec_kw={'width_ratios': [1.25, 1]})

# (a) transfer theorems solved by L_true bin
a = ax[0]
TOK = {'s0': {7: 140, 8: 137, 9: 300, 10: 34, 11: 1, 12: 0}, 's1': {7: 139, 8: 138, 9: 312, 10: 34, 11: 0, 12: 0}}     # ladder.md (branch dan_ladder_a), la_T1_s0 / s1
NB = {int(k): v for k, v in S['transfer_bin_sizes'].items()}
bins = [7, 8, 9, 10, 11, 12]
for s in ('s0', 's1'):
    a.plot(bins, [TOK[s][L] / NB[L] for L in bins], color=COL['token'], lw=2, marker='o', ms=3.5, label=NAME['token'] + ' T1 (L* 10 / 10)' if s == 's0' else None)
for m in ('seed0', 'seed2'):
    ls = [P3[f'{m}_T1_s{s}']['lstar_transfer'] for s in (0, 1) if f'{m}_T1_s{s}' in P3]
    for s in (0, 1):
        v = P3.get(f'{m}_T1_s{s}')
        if v:
            bb = {int(k): c for k, c in v['transfer_by_bin'].items()}
            a.plot(bins, [bb.get(L, 0) / NB[L] for L in bins], color=COL[m], lw=2, marker='o', ms=3.5, label=NAME[m] + f" T1 (L* {' / '.join(map(str, ls))})" if s == 0 else None)
        v = P3.get(f'{m}_frozen_s{s}')
        if v:
            bb = {int(k): c for k, c in v['transfer_by_bin'].items()}
            a.plot(bins, [bb.get(L, 0) / NB[L] for L in bins], color=COL[m], lw=1.3, ls=(0, (4, 2)))
a.plot([], [], color=MUTED, ls=(0, (4, 2)), lw=1.3, label='frozen Lean controls, same attempts (token frozen: L* 7)')
a.axvline(10.5, color='#c9c8c2', lw=0.8); a.text(10.55, 0.66, 'L_true ≥ 11: the\nL* = 11 threshold', fontsize=7, color=MUTED, va='top')
a.set_xlabel('minimal proof length L_true of the transfer theorem (bin sizes 300 / 300 / 1,010 / 451 / 99 / 102)'); a.set_ylabel('fraction solved in 256 attempts')
a.set_title('(a) Ladder rung T1, transfer pool (2,285 theorems; never trained on), round 8', fontsize=9, loc='left'); a.grid(axis='y', color='#e6e5e0', lw=0.6); a.set_ylim(-0.02, 0.72)
a.legend(frameon=False, fontsize=7.2, loc='upper right')

# (b) L* by round
b = ax[1]
off = {'seed0': -0.06, 'seed2': 0.06}
for m in ('seed0', 'seed2'):
    for s in (0, 1):
        v = P3.get(f'{m}_T1_s{s}')
        if v:
            r = [x[0] for x in v['lstar_by_round']]; y = [x[1] + off[m] for x in v['lstar_by_round']]
            b.plot(r, y, color=COL[m], lw=2, marker='o', ms=3.5, alpha=1 if s == 0 else 0.6, label=NAME[m].split(',')[1].strip() + f' T1, EI seed {s}')
        v = P3.get(f'{m}_frozen_s{s}')
        if v:
            r = [x[0] for x in v['lstar_by_round']]; y = [x[1] + off[m] for x in v['lstar_by_round']]
            b.plot(r, y, color=COL[m], lw=1.3, ls=(0, (4, 2)), alpha=1 if s == 0 else 0.6)
b.axhline(10, color=COL['token'], lw=1.3, ls=(0, (1, 2))); b.text(8.6, 10.08, 'token T1 (round 8)', fontsize=7, color=MUTED, ha='right')
b.set_xlabel('EI round (32 attempts per target each; cumulative)'); b.set_ylabel('transfer L*  (max L with ≥ 5 theorems solved at L_true ≥ L)')
b.set_title('(b) Transfer L* by round (dashed: frozen)', fontsize=9, loc='left'); b.grid(axis='y', color='#e6e5e0', lw=0.6); b.set_yticks([8, 9, 10, 11, 12]); b.set_ylim(7.6, 12.4)
b.legend(frameon=False, fontsize=7.2, loc='lower right')
fig.tight_layout(); fig.savefig('figures/lean_seed2.png', dpi=160)
print('figures/lean_seed2.png')
