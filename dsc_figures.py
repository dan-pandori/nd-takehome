#!/usr/bin/env python3
"""ds-composition figures from artifacts/dsc/summary.json (dsc_analysis.py):
  figures/dsc_heldout.png    held-out greedy by length per arm (both seeds; 6-line bin split no-pattern / pattern)
  figures/dsc_readiness.png  readiness panel per arm: depth-3 pass@2,000 (req8 pool), reductio-req pass@2,000, dial EI - frozen, ladder frozen / T1 solved, L*
Palette: dataviz reference slots (categorical), C0 in neutral grey, A3 (cap 8) hatched as the yardstick."""
import json, os, sys
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

S = json.load(open('artifacts/dsc/summary.json'))
ARMS = [('c0', 'C0 control'), ('a1', 'A1 natural hist.'), ('a2', 'A2 rule quotas'), ('a3', 'A3 cap 8 (yardstick)'), ('a4', 'A4 cap-heavy')]
COL = {'c0': '#6b7280', 'a1': '#2563eb', 'a2': '#d97706', 'a3': '#7c3aed', 'a4': '#059669'}
os.makedirs('figures', exist_ok=True)
rows = S['rows']

# ---- figure 1: held-out by length
fig, axes = plt.subplots(1, 2, figsize=(11, 4), gridspec_kw={'width_ratios': [3, 1.6]})
ax = axes[0]
for arm, label in ARMS:
    for s, ls in ((0, '-'), (1, '--')):
        h = rows.get(f'{arm}_s{s}', {}).get('heldout')
        if not h:
            continue
        L = sorted(int(k) for k in h['by_len'])
        ax.plot(L, [h['by_len'][str(k)] for k in L], ls, marker='o', ms=4, color=COL[arm], label=f'{label} s{s}' if s == 0 else None, alpha=0.9 if s == 0 else 0.6)
ax.set_xlabel('held-out theorem length (generator proof lines)'); ax.set_ylabel('greedy accuracy (Lean ∧ nd_verify)'); ax.set_ylim(0.3, 1.01); ax.set_xticks([2, 3, 4, 5, 6])
ax.set_title('Stage-1 held-out greedy by length (solid s0, dashed s1)', fontsize=10); ax.legend(fontsize=8, loc='lower left'); ax.grid(alpha=0.3)
ax = axes[1]
x = np.arange(len(ARMS)); w = 0.2
for i, (arm, label) in enumerate(ARMS):
    for s in (0, 1):
        h = rows.get(f'{arm}_s{s}', {}).get('heldout')
        if not h:
            continue
        np_ = h['by_len_pattern'].get('6_nopat', {}).get('rate', 0); pa = h['by_len_pattern'].get('6_pat', {}).get('rate', 0)
        ax.bar(i + (s - 0.5) * w * 1.1, np_, w, color=COL[arm], alpha=0.9 if s == 0 else 0.55, hatch='//' if arm == 'a3' else None, edgecolor='white')
        ax.plot([i + (s - 0.5) * w * 1.1], [pa], marker='x', color='black', ms=6)
ax.set_xticks(x); ax.set_xticklabels([a.upper() for a, _ in ARMS], fontsize=8); ax.set_ylim(0.3, 1.0); ax.grid(alpha=0.3, axis='y')
ax.set_title('6-line bin: no-pattern (bars) and pattern (x)', fontsize=10)
plt.tight_layout(); plt.savefig('figures/dsc_heldout.png', dpi=150); plt.close()

# ---- figure 2: readiness panel
panels = [('depth-3 req8 pass@2,000\n(targets with a depth-3 proof, of 300)', lambda r: (r['coverage'].get('d3req') or {}).get('solved_with_pattern')),
          ('reductio-req pass@2,000\n(targets solved, of 300)', lambda r: (r['coverage'].get('redreq') or {}).get('solved')),
          ('dial round 4: EI − frozen\n(depth-3 acquisition)', lambda r: r.get('dial_ei_minus_frozen')),
          ('ladder frozen: transfer solved\n(of 2,285)', lambda r: (r.get('ladder_frozen') or {}).get('transfer', {}).get('solved')),
          ('ladder T1: transfer solved\n(of 2,285)', lambda r: (r.get('ladder_T1') or {}).get('transfer', {}).get('solved')),
          ('ladder T1: transfer L*', lambda r: (r.get('ladder_T1') or {}).get('transfer', {}).get('lstar'))]
fig, axes = plt.subplots(1, len(panels), figsize=(16, 3.8))
for ax, (title, f) in zip(axes, panels):
    for i, (arm, label) in enumerate(ARMS):
        for s in (0, 1):
            r = rows.get(f'{arm}_s{s}')
            v = f(r) if r else None
            if v is None:
                continue
            ax.bar(i + (s - 0.5) * 0.22, v, 0.2, color=COL[arm], alpha=0.9 if s == 0 else 0.55, hatch='//' if arm == 'a3' else None, edgecolor='white')
    ax.set_xticks(range(len(ARMS))); ax.set_xticklabels([a.upper() for a, _ in ARMS], fontsize=8); ax.set_title(title, fontsize=9); ax.grid(alpha=0.3, axis='y')
    ax.axhline(0, color='black', lw=0.5)
fig.suptitle('RL readiness per arm (left bar s0, right bar s1; A3 hatched = cap 8, outside the take-home rule)', fontsize=10)
plt.tight_layout(); plt.savefig('figures/dsc_readiness.png', dpi=150); plt.close()
print('figures written')
