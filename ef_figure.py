#!/usr/bin/env python3
"""Run efficiency: the write-up figure — decoded tokens per sample and samples/s, before and after."""
import json, glob, os, sys
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

A = 'artifacts/ef'
LADDER = json.load(open(f'{A}/ladder.json')) if os.path.exists(f'{A}/ladder.json') else None
d = {os.path.basename(f)[:-5]: json.load(open(f)) for f in glob.glob(f'{A}/*.json') if 'tokens' not in f}

ROWS = [('base_orig', 'before\n(batch 512)'), ('r_eos_mn288', 'after: fixes\n(batch 512)'),
        ('r_rec', 'after: fixes\n+ batch 4096')]
rows = [(d[k], lab) for k, lab in ROWS if k in d]

fig, ax = plt.subplots(1, 3, figsize=(11.5, 3.6))
C = ['#7b8794', '#2f6fb3', '#1a9e6f']

lab = [l for _, l in rows]
x = np.arange(len(rows))

sps = [r['samples_per_s'] for r, _ in rows]
ax[0].bar(x, sps, color=C[:len(rows)], width=.6)
for i, v in enumerate(sps):
    ax[0].text(i, v, f'{v:,.0f}\n({v/sps[0]:.1f}x)', ha='center', va='bottom', fontsize=9)
ax[0].set_ylabel('samples / second'); ax[0].set_title('sampler throughput', fontsize=10)
ax[0].set_ylim(0, max(sps) * 1.32)

tk = [r['decoded_tokens_mean'] for r, _ in rows]
p95 = [r['decoded_tokens_p95'] for r, _ in rows]
ax[1].bar(x - .17, tk, width=.34, color=C[:len(rows)], label='mean')
ax[1].bar(x + .17, p95, width=.34, color=C[:len(rows)], alpha=.45, label='p95')
for i, (a_, b_) in enumerate(zip(tk, p95)):
    ax[1].text(i - .17, a_, f'{a_:.0f}', ha='center', va='bottom', fontsize=8)
    ax[1].text(i + .17, b_, f'{b_:.0f}', ha='center', va='bottom', fontsize=8)
ax[1].set_ylabel('decoded tokens per sample'); ax[1].set_title('tokens per sample (mean, p95)', fontsize=10)
ax[1].legend(fontsize=8, frameon=False)
ax[1].set_ylim(0, max(p95) * 1.45)

st = [r['rowsteps'] / 1e6 for r, _ in rows]
ms = [r['model_steps'] / 1e3 for r, _ in rows]
ax[2].bar(x - .17, st, width=.34, color=C[:len(rows)], label='row-steps (M)')
ax[2].bar(x + .17, ms, width=.34, color=C[:len(rows)], alpha=.45, label='decode steps (k)')
for i, (a_, b_) in enumerate(zip(st, ms)):
    ax[2].text(i - .17, a_, f'{a_:.1f}', ha='center', va='bottom', fontsize=8)
    ax[2].text(i + .17, b_, f'{b_:.1f}', ha='center', va='bottom', fontsize=8)
ax[2].set_title('work done and kernel launches', fontsize=10)
ax[2].legend(fontsize=8, frameon=False)
ax[2].set_ylim(0, max(st + ms) * 1.45)

for a_ in ax:
    a_.set_xticks(x); a_.set_xticklabels([f'[{i+1}] ' + l for i, l in enumerate(lab)], fontsize=9)
    a_.spines['top'].set_visible(False); a_.spines['right'].set_visible(False)
fig.suptitle('run efficiency — 200 ladder-transfer targets (L_true 7–12), k = 256, 51,200 samples, RTX 3090', fontsize=10)
note = '      '.join(f"[{i+1}] end to end {r.get('end_to_end_s', float('nan')):.0f} s, peak {r['peak_alloc_gb']:.1f} GB"
                     for i, (r, _) in enumerate(rows))
fig.text(.5, .055, note, ha='center', fontsize=8.5, color='#333')
fig.text(.5, .022, 'tokens per sample barely move: this model already terminated on 99.99 % of rows — the cost was '
                   'the number of decode steps, and the memory that caps the batch', ha='center', fontsize=8, color='#666')
fig.tight_layout(rect=[0, .095, 1, .94])
os.makedirs('figures', exist_ok=True)
fig.savefig('figures/efficiency_before_after.png', dpi=160)
print('wrote figures/efficiency_before_after.png', [r['tag'] for r, _ in rows])
