#!/usr/bin/env python3
"""grpo-best figure from artifacts/gb/summary.json (gb_analysis.py): (a) group-C theorems solved at k 256 (sample seed 1)
per round-equivalent, per arm (seed dots, mean line); (b) group B pass@1 against pass@256 at r8 (sample seed 1), per seed.
-> figures/grpo_best.png"""
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

S = json.load(open('artifacts/gb/summary.json'))['arms']
ARMS = [('EI', 'EI (trajectory T1)', '#2a78d6', 'o'), ('default', 'GRPO default', '#eb6834', 's'),
        ('unlikely', 'GRPO unlikely', '#1baf7a', '^'), ('passk', 'GRPO pass@4', '#eda100', 'D'),
        ('distinct', 'GRPO distinct', '#e87ba4', 'v')]
fig, (a1, a2) = plt.subplots(1, 2, figsize=(11, 4.2))
for i, (k, lab, c, m) in enumerate(ARMS):
    xs, ys = [], []
    for j, ck in enumerate(('r2', 'r4', 'r8')):
        v = S.get(k, {}).get(f'C_{ck}_x1')
        if not v or any(x is None for x in v):
            continue
        off = (i - 2) * 0.06
        a1.scatter([j + off] * len(v), v, color=c, marker=m, s=22, alpha=0.6, linewidths=0)
        xs.append(j + off); ys.append(sum(v) / len(v))
    if xs:
        a1.plot(xs, ys, color=c, lw=2, marker=m, ms=8, label=lab)
    v = S.get(k, {}).get('B_r8_pass1_pass256_x1')
    if v:
        a2.scatter(v[1], v[0], color=c, marker=m, s=64, label=lab, edgecolors='white', linewidths=1.5)
a1.set_xticks([0, 1, 2]); a1.set_xticklabels(['r2', 'r4', 'r8'])
a1.set_xlabel('round-equivalent (equal target attempts)'); a1.set_ylabel('group C theorems solved (k 256)')
a1.set_title('(a) Group C (EI never solved): solves per seed, line = mean', fontsize=10)
a2.set_xlabel('group B pass@256 at r8'); a2.set_ylabel('group B pass@1 at r8')
a2.set_title('(b) Group B at r8: sharpening (y) vs coverage (x), per seed', fontsize=10)
for ax in (a1, a2):
    ax.grid(color='#e5e5e5', lw=0.8); ax.set_axisbelow(True)
    for s in ('top', 'right'):
        ax.spines[s].set_visible(False)
a1.legend(fontsize=8, frameon=False)
fig.suptitle('grpo-best: best-cap12 s0–s2 (ALiBiGPT 9.56M, lean_staten, K12); Lean alone; sample seed 1', fontsize=10)
fig.tight_layout()
fig.savefig('figures/grpo_best.png', dpi=130)
print('figures/grpo_best.png')
