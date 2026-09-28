#!/usr/bin/env python3
"""Figure for run `state-frontier`: python3 sf_figures.py  ->  figures/state_frontier.png
Left: per-theorem success rate at k = 256 on the 224 transfer theorems with L_true >= 11, state-conditioned T1 finals
(S + SN, mean over checkpoints) against the whole-proof control C0's T1 finals.  Right: held-out greedy depth-3 slice
per Stage-1 seed, state-conditioned seeds against the control configuration's 52 cells (NOISE_FLOOR.md)."""
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

S = json.load(open('artifacts/sf2/summary.json'))
rows = {}
for lab in S['q1']['state_T1_models'] + S['q1']['c0_T1_models']:
    fn = lab + '_mn1024' if S['resample']['models'][lab].get('rerun_of_max_new_512') else lab
    rows[lab] = {r['name']: r for r in map(json.loads, open(f'artifacts/sf2/rs/{fn}.jsonl'))}
st, c0 = S['q1']['state_T1_models'], S['q1']['c0_T1_models']
INK, MUTED, GRID = '#1f1f1e', '#6b6a64', '#e4e3dc'
COL = {11: '#2a78d6', 12: '#eb6834', 13: '#1baf7a'}          # reference palette slots 1-3, fixed order
MK = {11: 'o', 12: 's', 13: '^'}
fig, (a, b) = plt.subplots(1, 2, figsize=(11.5, 4.8), gridspec_kw={'width_ratios': [1.15, 1]})
eps = 0.25 / 256
for Lb in (11, 12, 13):
    xs, ys = [], []
    for n, r in rows[st[0]].items():
        if (r['L_true'] if r['L_true'] < 13 else 13) != Lb:
            continue
        x = sum(rows[l][n]['n_ok'] for l in c0) / (256 * len(c0)); y = sum(rows[l][n]['n_ok'] for l in st) / (256 * len(st))
        if x or y:
            xs.append(max(x, eps)); ys.append(max(y, eps))
    lab = f"L_true {Lb}" if Lb < 13 else "L_true 13-14"
    a.scatter(xs, ys, s=30, c=COL[Lb], marker=MK[Lb], edgecolors='white', linewidths=1, label=f'{lab} ({len(xs)} solved by either)', zorder=3)
a.plot([eps, 1], [eps, 1], color=MUTED, lw=1, ls='--', zorder=1)
a.set_xscale('log'); a.set_yscale('log'); a.set_xlim(eps / 1.5, 1); a.set_ylim(eps / 1.5, 1)
a.axvline(eps, color=GRID, lw=1); a.axhline(eps, color=GRID, lw=1)
a.set_xlabel(f'whole-proof C0 T1: success rate per theorem (mean of {len(c0)})', color=INK)
a.set_ylabel(f'state T1 (S, SN): success rate (mean of {len(st)})', color=INK)
a.set_title('Per-theorem success at k = 256, L_true ≥ 11\n(points on the grey lines: 0 successes)', color=INK, fontsize=10)
a.legend(frameon=False, fontsize=8, loc='lower right')
L = S['q2_lottery']
ctrl = sorted(L['control']['values'])
b.scatter([0 + (i % 7 - 3) * 0.03 for i in range(len(ctrl))], ctrl, s=22, c='#9a998f', edgecolors='white', linewidths=1, zorder=3)
old = [v['depth3_rate'] for v in L['seeds'].values() if not v['new']]
new = [(k, v['depth3_rate']) for k, v in L['seeds'].items() if v['new']]
b.scatter([1 + (i - len(old) / 2) * 0.04 for i in range(len(old))], old, s=34, c='#2a78d6', marker='o', edgecolors='white', linewidths=1, zorder=3)
b.scatter([2 + (i - len(new) / 2) * 0.04 for i in range(len(new))], [v for _, v in new], s=40, c='#eb6834', marker='D', edgecolors='white', linewidths=1, zorder=3)
b.axhline(L['threshold'], color=MUTED, lw=1, ls='--'); b.text(2.45, L['threshold'] + 0.01, 'high mode > 0.44', color=MUTED, fontsize=8, ha='right')
b.set_xticks([0, 1, 2]); b.set_xticklabels([f"control config\n{L['control']['high']}/{L['control']['n']} high",
                                           f"state, on file\n{sum(v > 0.44 for v in old)}/{len(old)} high",
                                           f"state, new seeds\n{L['new_high']}/{L['new_n']} high"], fontsize=9)
b.set_xlim(-0.5, 2.5); b.set_ylim(0, 1); b.set_ylabel('held-out greedy, depth-3 slice (500)', color=INK)
b.set_title('Depth-3 slice per Stage-1 seed', color=INK, fontsize=10)
for ax in (a, b):
    ax.grid(True, color=GRID, lw=0.6, zorder=0)
    for s in ('top', 'right'):
        ax.spines[s].set_visible(False)
    ax.tick_params(colors=MUTED, labelsize=8)
fig.tight_layout(); fig.savefig('figures/state_frontier.png', dpi=150)
print('figures/state_frontier.png')
