#!/usr/bin/env python3
"""Figure for run lean-only from artifacts/lo/summary.json (python3 lean_only_analysis.py phase2 first) -> figures/lean_only.png
Four panels, fragment (blue) vs free-form (orange), one dot per seed, token/on-file comparators in grey:
  (a) Stage-1 held-out greedy and transfer pass@16;  (b) depth-3: base rate at pass@2,000, EI and frozen acquisition at round 8;
  (c) ladder transfer L* in lines and in term size (T1 and frozen);  (d) tokens per accepted proof (log scale)."""
import json, os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

S = json.load(open('artifacts/lo/summary.json'))
C = {'seq': '#2a78d6', 'free': '#eb6834', 'ref': '#8a8985'}
LBL = {'seq': 'fragment (have)', 'free': 'free-form'}
os.makedirs('figures', exist_ok=True)
fig, ax = plt.subplots(1, 4, figsize=(15, 3.9))
for a in ax:
    a.spines[['top', 'right']].set_visible(False); a.grid(axis='y', color='#e6e6e3', lw=0.8); a.set_axisbelow(True)


def dots(a, x, fmt, vals, label=None):
    for k, v in enumerate(vals):
        if v is None: continue
        a.plot([x + (k - 0.5) * 0.12], [v], 'o', ms=7, color=C[fmt], mec='white', mew=1.2, label=label if k == 0 else None)


# (a) Stage-1
st = S['stage1']; a = ax[0]
for i, (key, name) in enumerate((('heldout', 'held-out greedy'), ('transfer_k16', 'transfer pass@16'))):
    for j, fmt in enumerate(('seq', 'free')):
        vals = [st.get(f'stage1_full_{fmt}_s{s}', {}).get(key, {}).get('rate') for s in (0, 1)]
        dots(a, i * 2 + j * 0.6, fmt, vals, LBL[fmt] if i == 0 else None)
    ref = {'heldout': 0.936, 'transfer_k16': 0.571}[key]
    a.hlines(ref, i * 2 - 0.3, i * 2 + 0.9, color=C['ref'], lw=1.2, ls='--', label='lean_seq on file (proposal 8)' if i == 0 else None)
a.set_xticks([0.3, 2.3]); a.set_xticklabels(['held-out greedy', 'transfer pass@16']); a.set_ylim(0.35, 1.0); a.set_title('(a) Stage-1 accuracy', loc='left', fontsize=10)
a.legend(frameon=False, fontsize=8, loc='lower left')
# (b) depth-3
b = ax[1]; br = S['base_rates_k2000']; d3 = S['depth3_dial']
for j, fmt in enumerate(('seq', 'free')):
    dots(b, 0 + j * 0.6, fmt, [br.get(f'{fmt}_s{s}', {}).get('depth3_nd_rate') for s in (0, 1)])
    dots(b, 2 + j * 0.6, fmt, [d3.get(f'frozen_d3_{fmt}_s{s}', {}).get('acq_targets') for s in (0, 1)])
    dots(b, 4 + j * 0.6, fmt, [d3.get(f'ei_d3_{fmt}_s{s}', {}).get('acq_targets') for s in (0, 1)])
for x, ref in ((2, (0.206, 0.134)), (4, (0.476, 0.479))):
    for r in ref: b.hlines(r, x - 0.3, x + 0.9, color=C['ref'], lw=1.2, ls='--')
b.hlines(0.005, 4 - 0.3, 4 + 0.9, color='#0b0b0b', lw=1.2, ls=':', label='token EI frozen (0.005)')
b.set_xticks([0.3, 2.3, 4.3]); b.set_xticklabels(['base rate\npass@2,000', 'frozen r8\n(256 attempts)', 'EI r8']); b.set_ylim(0, 1.0)
b.set_title('(b) depth-3 targets with a depth-3 proof', loc='left', fontsize=10)
# (c) ladder L*
c = ax[2]; la = S['ladder']
for i, (key, name) in enumerate((('lstar_lines', 'L* lines'), ('lstar_ts', 'L* term size'))):
    for j, fmt in enumerate(('seq', 'free')):
        dots(c, i * 2.4 + j * 0.6, fmt, [la.get(f'la_T1_{fmt}_s{s}', {}).get(key) for s in (0, 1)])
        fr = [la.get(f'la_frozen_{fmt}_s{s}', {}).get(key) for s in (0, 1)]
        for k, v in enumerate(fr):
            if v is not None: c.plot([i * 2.4 + j * 0.6 + (k - 0.5) * 0.12], [v], 'o', ms=7, mfc='white', mec=C[fmt], mew=1.5)
c.hlines(11, -0.3, 0.9, color=C['ref'], lw=1.2, ls='--'); c.hlines(10, -0.3, 0.9, color='#0b0b0b', lw=1.2, ls=':')
c.set_xticks([0.3, 2.7]); c.set_xticklabels(['transfer L* (lines)', 'transfer L* (term size)']); c.set_ylim(4, 14)
c.set_title('(c) ladder T1: filled = EI, hollow = frozen', loc='left', fontsize=10)
# (d) tokens per accepted proof
d = ax[3]
for j, fmt in enumerate(('seq', 'free')):
    dots(d, 0 + j * 0.6, fmt, [st.get(f'stage1_full_{fmt}_s{s}', {}).get('heldout', {}).get('tokens_per_accepted_proof') for s in (0, 1)])
    dots(d, 2 + j * 0.6, fmt, [la.get(f'la_T1_{fmt}_s{s}', {}).get('tokens_per_proof') for s in (0, 1)])
d.set_yscale('log'); d.set_xticks([0.3, 2.3]); d.set_xticklabels(['held-out proofs', 'ladder transfer proofs']); d.set_title('(d) tokens per accepted proof', loc='left', fontsize=10)
fig.suptitle('lean-only: free-form terms vs the have-fragment under lean_check (dots = Stage-1 seeds 0, 1; grey dashes = proposal-8 lean_seq on file)', fontsize=10, x=0.01, ha='left')
fig.tight_layout(rect=(0, 0, 1, 0.94))
fig.savefig('figures/lean_only.png', dpi=150)
print('figures/lean_only.png')
