#!/usr/bin/env python3
"""support-followups figures.  figures/sf_d_steps.png (D) and figures/sf_c_reach.png (C)."""
import json, os, collections
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

INK, INK2, GRID, SURF = '#0b0b0b', '#52514e', '#e4e3df', '#fcfcfb'
COL = {'S': '#2a78d6', 'C1': '#eb6834', 'C2': '#1baf7a', 'C3': '#eda100'}
LAB = {'S': 'S: EI proofs of the 29 survivors', 'C1': 'C1: EI proofs, other forward crux',
       'C2': "C2: base's own proofs (stage 1)", 'C3': "C3: base's own proofs, forward crux"}
plt.rcParams.update({'font.size': 9, 'axes.edgecolor': INK2, 'axes.labelcolor': INK, 'xtick.color': INK2, 'ytick.color': INK2,
                     'axes.spines.top': False, 'axes.spines.right': False, 'figure.facecolor': SURF, 'axes.facecolor': SURF})


def d_fig(path='artifacts/sf/d_steps.jsonl', out='figures/sf_d_steps.png'):
    R = [json.loads(l) for l in open(path)]
    best = {}
    for r in R:
        k = (r['set'], r['name'])
        if k not in best or r['base']['T1']['total'] > best[k]['base']['T1']['total']:
            best[k] = r
    fig, ax = plt.subplots(1, 2, figsize=(10, 3.8), gridspec_kw={'width_ratios': [1.3, 1]})
    K = 8
    for s in ('C2', 'C3', 'C1', 'S'):
        prof = [sorted(p['lp'] for p in r['base']['T1']['steps'])[:K] for (ss, _), r in best.items() if ss == s]
        prof = np.array([p + [0.0] * (K - len(p)) for p in prof])
        med = np.median(prof, 0); lo, hi = np.percentile(prof, 25, 0), np.percentile(prof, 75, 0)
        x = np.arange(1, K + 1)
        ax[0].fill_between(x, lo, hi, color=COL[s], alpha=0.15, lw=0)
        ax[0].plot(x, med, color=COL[s], lw=2, marker='o', ms=4, label=f'{LAB[s]} (n={len(prof)} theorems)')
    ax[0].set_xlabel('step rank within the proof (1 = least probable step)')
    ax[0].set_ylabel('base s0 log p of the step (nats, T 1.0)')
    ax[0].set_title('Sorted per-step log p, best proof per theorem (median, IQR)', color=INK, fontsize=9.5, loc='left')
    ax[0].axhline(-6, color=INK2, lw=0.8, ls=':'); ax[0].text(K, -6.3, 'pre-registered w1 cut −6', ha='right', va='top', color=INK2, fontsize=8)
    ax[0].grid(axis='y', color=GRID, lw=0.6); ax[0].legend(frameon=False, fontsize=7.5, loc='lower right')
    for s in ('C2', 'C3', 'C1', 'S'):
        pts = [(r['base']['T1']['total'] - r['base']['T1']['w1'], r['base']['T1']['w1']) for (ss, _), r in best.items() if ss == s]
        ax[1].scatter(*zip(*pts), s=22, color=COL[s], edgecolor=SURF, lw=0.8, label=s)
    ax[1].set_xlabel('log p of all other steps (nats)'); ax[1].set_ylabel('log p of the worst step (nats)')
    ax[1].set_title('Worst step vs the rest', color=INK, fontsize=9.5, loc='left')
    ax[1].grid(color=GRID, lw=0.6); ax[1].legend(frameon=False, fontsize=8, loc='lower left')
    fig.text(0.01, 0.005, 'Model: base s0 = stage1_a1_seq_s0.pt (md5 9bde44c0), 3.2 M params, from scratch, lean_seq, cap 6. '
             'Name offset marginalised exactly. Source: artifacts/sf/d_steps.jsonl', fontsize=7, color=INK2)
    fig.tight_layout(rect=(0, 0.03, 1, 1)); os.makedirs('figures', exist_ok=True); fig.savefig(out, dpi=150); print('->', out)


def c_fig(path='artifacts/sf/abc_summary.json', out='figures/sf_c_reach.png'):
    S = json.load(open(path))
    if 'C' not in S:
        print('no C yet'); return
    reach = S['C']['survivors']
    Ls = sorted({e['L_true'] for e in reach.values()})
    tot = [sum(1 for e in reach.values() if e['L_true'] == L) for L in Ls]
    big = [sum(e['reached'] for e in reach.values() if e['L_true'] == L) for L in Ls]
    fig, ax = plt.subplots(figsize=(6.4, 3.6))
    x = np.arange(len(Ls)); w = 0.26
    bars = [('EI s0 (3.2 M + 8×32 EI): solves', tot, '#2a78d6'),
            ('big s0 (25.3 M, same data & steps): reaches', big, '#eb6834'),
            ('base s0 (3.2 M): reaches', [0] * len(Ls), '#1baf7a')]
    for i, (lab, v, c) in enumerate(bars):
        b = ax.bar(x + (i - 1) * w, v, w - 0.03, color=c, label=lab)
        for xi, vi in zip(x + (i - 1) * w, v):
            ax.text(xi, vi + 0.15, str(vi), ha='center', va='bottom', fontsize=8, color=INK)
    ax.set_xticks(x, [f'L_true {L}' for L in Ls]); ax.set_ylabel('falsifier survivors')
    ax.set_title(f"The 29 survivors: big s0 reaches {S['C']['survivors_reached']} "
                 '(≤ 200,000 attempts per temperature, T 0.8 and 1.0)', color=INK, fontsize=9.5, loc='left')
    ax.grid(axis='y', color=GRID, lw=0.6); ax.set_axisbelow(True); ax.legend(frameon=False, fontsize=8)
    fig.text(0.01, 0.005, "Base s0: 0 in 400,000 (support-curves). big s0 md5 4efb5a1e; EI s0 md5 5cebd7ec. Lean alone judges.",
             fontsize=7, color=INK2)
    fig.tight_layout(rect=(0, 0.03, 1, 1)); fig.savefig(out, dpi=150); print('->', out)


if __name__ == '__main__':
    d_fig(); c_fig()
