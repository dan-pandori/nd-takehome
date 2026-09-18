#!/usr/bin/env python3
"""Figures for round3-run1 from artifacts/r3_1/summary.json: (1) final required-stratum acquisition and ignition round vs
pre-RL rate, pool as the marker, per pattern; (2) drift curves (pattern rate on the required pool per checkpoint);
(3) per-round required-stratum pattern theorems per arm."""
import json, math, os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

CAT = {'req': '#2a78d6', 'mix': '#eb6834', 'drift': '#1baf7a'}
MARK = {'req': 'o', 'mix': 's', 'drift': '^'}
INK2 = '#52514e'; ZERO_X = 3e-7
S = json.load(open('artifacts/r3_1/summary.json'))
os.makedirs('figures', exist_ok=True)


def _style(ax):
    for s in ('top', 'right'):
        ax.spines[s].set_visible(False)
    ax.grid(True, axis='y', color='#e6e5e1', linewidth=0.8)
    ax.tick_params(colors=INK2, labelsize=9)


def _x(r):
    return ZERO_X if not r else r


fig, axes = plt.subplots(2, 2, figsize=(11, 8))
for j, pat in enumerate(('depth3', 'reductio')):
    P = S[pat]
    for i, (key, lab) in enumerate((('final_pattern_required', 'required targets with a pattern proof, round 8'), ('ignition_round', 'ignition round (none = 9)'))):
        ax = axes[i][j]; _style(ax)
        for name, a in P['arms'].items():
            s, arm = name.split('_')
            d = P['draws'].get(s[1:])
            if not d or arm == 'drift':
                continue
            y = a[key] if a[key] is not None else (9 if key == 'ignition_round' else 0)
            ax.scatter(_x(d['rate']), y, marker=MARK[arm], color=CAT[arm], s=48, alpha=0.85, label=arm)
            ax.annotate(s, (_x(d['rate']), y), fontsize=7, color=INK2, xytext=(3, 3), textcoords='offset points')
        ax.set_xscale('log'); ax.set_xlim(ZERO_X / 2, 1e-2)
        ax.set_xlabel('pre-RL pattern rate per sample (0 drawn at the left edge)', fontsize=9, color=INK2)
        ax.set_ylabel(lab, fontsize=9, color=INK2)
        ax.set_title(f'{pat}: {lab.split(",")[0]} vs pre-RL rate', fontsize=10)
        h, l = ax.get_legend_handles_labels(); uniq = dict(zip(l, h)); ax.legend(uniq.values(), uniq.keys(), fontsize=8, frameon=False)
fig.tight_layout(); fig.savefig('figures/r3_1_ignition_vs_rate.png', dpi=150)

fig, axes = plt.subplots(1, 2, figsize=(11, 4))
for j, pat in enumerate(('depth3', 'reductio')):
    ax = axes[j]; _style(ax); P = S[pat]
    for s, d in P['drift'].items():
        rs = sorted(int(r) for r in d)
        ax.plot(rs, [d[str(r)]['hits'] for r in rs], marker='o', label=f's{s}' + (' (zero-rate)' if P['draws'].get(s, {}).get('zero_rate') else ''))
    ax.set_xlabel('drift-arm round (checkpoint)', fontsize=9, color=INK2); ax.set_ylabel('pattern hits on the required pool (k = 1,000 x 300)', fontsize=9, color=INK2)
    ax.set_title(f'{pat}: drift arms (neighbours only, pattern proofs excluded from training)', fontsize=10); ax.legend(fontsize=8, frameon=False)
fig.tight_layout(); fig.savefig('figures/r3_1_drift.png', dpi=150)

fig, axes = plt.subplots(1, 2, figsize=(11, 4))
for j, pat in enumerate(('depth3', 'reductio')):
    ax = axes[j]; _style(ax); P = S[pat]
    for name, a in P['arms'].items():
        s, arm = name.split('_')
        if arm == 'drift':
            continue
        z = P['draws'].get(s[1:], {}).get('zero_rate')
        ax.plot([p['round'] for p in a['per_round']], [p['pattern_required'] for p in a['per_round']], color=CAT[arm], marker=MARK[arm], ms=3,
                alpha=0.9 if z else 0.35, linestyle='-' if z else '--')
    ax.set_xlabel('round', fontsize=9, color=INK2); ax.set_ylabel('required targets with a pattern proof (cumulative)', fontsize=9, color=INK2)
    ax.set_title(f'{pat}: req (blue) vs mix (orange); solid = zero-rate draw', fontsize=10)
fig.tight_layout(); fig.savefig('figures/r3_1_curves.png', dpi=150)
print('figures written')
