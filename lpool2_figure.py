#!/usr/bin/env python3
"""long-pool-2 figure: solve rate (k 256) by length stratum and by construction length, per model; 91 theorems
(21 new + 70 calibration), rows artifacts/lpool2/rr/<stem>__{new,cal}.jsonl.  -> figures/lpool2_rate.png"""
import json, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

pool = [json.loads(l) for l in open('data/ladder/transfer_long2.jsonl')] + [json.loads(l) for l in open('data/ladder/transfer_long2_calib.jsonl')]
MODELS = [('SN-cap12 T1', 'T1_SN12_s{}', 4, '#2a78d6', 'o'), ('SN-cap12 frozen', 'stage1_SN12_s{}', 4, '#eb6834', 's'),
          ('K12 whole-proof T1', 'T1_K12_s{}', 2, '#1baf7a', '^'), ('SN-v2 cap-6 T1', 'T1_SNv2_s{}', 2, '#eda100', 'D')]
strat = lambda r: 'L = 17' if r['stratum'] == '17' else 'L ≥ 18'
cons = lambda r: '≤ 28' if r['construction_pruned'] <= 28 else '29–32' if r['construction_pruned'] <= 32 else '33–36' if r['construction_pruned'] <= 36 else '≥ 37'
PANELS = [('Length stratum (minlen)', strat, ['L = 17', 'L ≥ 18']), ('Construction length (brief\'s upper bound)', cons, ['≤ 28', '29–32', '33–36', '≥ 37'])]
fig, axes = plt.subplots(1, 2, figsize=(10, 4.2), sharey=True, gridspec_kw={'width_ratios': [2, 4]})
fig.patch.set_facecolor('#fcfcfb')
for ax, (title, key, cats) in zip(axes, PANELS):
    ns = {c: sum(1 for r in pool if key(r) == c) for c in cats}
    for label, stem, nseed, col, mk in MODELS:
        per = []
        for s in range(nseed):
            solved = {}
            for tag in ('new', 'cal'):
                for l in open(f'artifacts/lpool2/rr/{stem.format(s)}__{tag}.jsonl'):
                    x = json.loads(l); solved[x['name']] = x['solved']
            per.append([100 * sum(solved[r['name']] for r in pool if key(r) == c) / ns[c] for c in cats])
        xs = range(len(cats))
        for p in per:
            ax.plot(xs, p, color=col, lw=0.8, alpha=0.35, marker=mk, ms=4)
        mean = [sum(p[i] for p in per) / len(per) for i in xs]
        ax.plot(xs, mean, color=col, lw=2, marker=mk, ms=8, markeredgecolor='#fcfcfb', markeredgewidth=2, label=f'{label} ({nseed} seeds)')
        if ax is axes[1]:
            ax.annotate(label, (xs[-1], mean[-1]), xytext=(8, {'SN-v2 cap-6 T1': 5, 'K12 whole-proof T1': -7}.get(label, 0)), textcoords='offset points', va='center', fontsize=8, color='#52514e')
    ax.axhline(10, color='#52514e', lw=0.8, ls=':')
    ax.set_xticks(range(len(cats))); ax.set_xticklabels([f'{c}\n(n {ns[c]})' for c in cats], fontsize=9, color='#52514e')
    ax.set_title(title, fontsize=10, color='#0b0b0b', loc='left')
    ax.set_facecolor('#fcfcfb'); ax.grid(axis='y', color='#e6e5e0', lw=0.6)
    for sp in ('top', 'right'): ax.spines[sp].set_visible(False)
    ax.set_xlim(-0.3, len(cats) - 0.3 + (1.2 if ax is axes[1] else 0))
axes[0].set_ylabel('theorems solved at k 256 (%)', color='#52514e'); axes[0].set_ylim(0, 100)
axes[0].text(-0.28, 11.5, '10 %', fontsize=8, color='#52514e')
axes[0].legend(fontsize=8, frameon=False, loc='upper right')
fig.suptitle('long-pool-2: 91 theorems with minlen ≥ 17 (21 new + 70 calibration); thin lines = seeds, thick = mean', fontsize=10, x=0.01, ha='left')
fig.tight_layout(); fig.savefig('figures/lpool2_rate.png', dpi=150)
