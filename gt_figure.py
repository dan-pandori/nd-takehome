#!/usr/bin/env python3
"""gt_figure.py -- figures/guided_tts.png from artifacts/gt/analysis.json (gt_analysis.py).

Rows: matched sampled tokens, matched wall-clock.  Columns: cap 12, cap 6 (trajectory / trajectory-cap6 r8 models,
9.56M ALiBiGPT, lean_staten).  Group: `long` (release theorems with min_lines > 10, n = 90) and `tb72`.  Thin lines:
seeds 0-2; thick: seed mean.  x: plain-equivalent attempts k (log2).
"""
import json, sys
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

A = json.load(open(sys.argv[1] if len(sys.argv) > 1 else 'artifacts/gt/analysis.json'))
OUT = sys.argv[2] if len(sys.argv) > 2 else 'figures/guided_tts.png'
KS = A['ks']
COL = {'plain': '#2a78d6', 'structural': '#eb6834', 'logical': '#1baf7a'}
MK = {'plain': 'o', 'structural': 's', 'logical': '^'}
LAB = {'plain': 'plain', 'structural': 'guided-structural', 'logical': 'guided-logical'}
CAPS = [('best12', 'cap 12'), ('best6', 'cap 6')]
groups = [g for g in ('long', 'tb72') if any(k.endswith('|' + g) for k in A['cells'])]
rows = [(g, kd) for g in groups for kd in ('tokens', 'wall')]
fig, axs = plt.subplots(len(rows), 2, figsize=(10, 3.2 * len(rows)), sharex=True, squeeze=False)
for r, (g, kd) in enumerate(rows):
    for c, (m, cap) in enumerate(CAPS):
        ax = axs[r][c]
        ends = []
        for arm in ('plain', 'structural', 'logical'):
            ys = [A['cells'][f'{m}|{s}|{arm}|{g}'][kd] for s in (0, 1, 2) if f'{m}|{s}|{arm}|{g}' in A['cells']
                  and not (kd == 'wall' and A['jobs'][f'{m}_s{s}_{arm}'].get('batch', 2048) != 2048)]   # batch-1,024 redo: wall not comparable
            if not ys:
                continue
            for y in ys:
                ax.plot(KS, [100 * v for v in y], color=COL[arm], lw=0.8, alpha=0.35)
            mean = [100 * sum(v) / len(ys) for v in zip(*ys)]
            ax.plot(KS, mean, color=COL[arm], lw=2, marker=MK[arm], ms=6, label=f'{LAB[arm]} ({len(ys)} seeds)')
            ends.append((mean[-1], LAB[arm]))
        lo, hi = ax.get_ylim(); gap = 0.06 * (hi - lo); prev = None
        for y, lab in sorted(ends):                    # direct labels, pushed apart so they never overlap
            y = y if prev is None else max(y, prev + gap); prev = y
            ax.annotate(lab, (KS[-1], y), xytext=(6, 0), textcoords='offset points', fontsize=7, color='#333333', va='center')
        ax.set_xscale('log', base=2)
        ax.set_xticks(KS); ax.set_xticklabels([str(k) for k in KS])
        ax.grid(alpha=0.25, lw=0.5)
        for sp in ('top', 'right'):
            ax.spines[sp].set_visible(False)
        ax.set_title(f'{cap} r8 — {g} — matched {"sampled tokens" if kd == "tokens" else "wall-clock"}', fontsize=9)
        if c == 0:
            ax.set_ylabel('solve rate (%)')
        if r == len(rows) - 1:
            ax.set_xlabel('budget, in plain attempts per theorem (k)')
        ax.set_xlim(1, 600)
axs[0][0].legend(fontsize=7, frameon=False, loc='lower right')
fig.suptitle('guided-tts: guided redraws vs plain resampling at matched compute (Lean judges every proof)\n'
             'models: trajectory(-cap6) la_T1_best{12,6}_s{0,1,2}_r8 (9.56M ALiBiGPT, lean_staten); cap-12 structural wall panels: '
             's1, s2 only (s0 ran at batch 1,024)', fontsize=9)
fig.tight_layout()
fig.savefig(OUT, dpi=150)
print('wrote', OUT)
