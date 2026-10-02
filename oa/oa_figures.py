#!/usr/bin/env python3
"""organism-analysis figures -> organism/figures/*.png (from artifacts/oa/*.json and data/oa/q2_steps.jsonl)."""
import json, os, sys
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

COL = ['#2a78d6', '#eb6834', '#1baf7a', '#eda100', '#e87ba4', '#008300', '#4a3aa7', '#e34948']   # fixed order
INK, INK2, GRID = '#0b0b0b', '#52514e', '#e4e3df'
plt.rcParams.update({'font.size': 9, 'axes.edgecolor': INK2, 'axes.labelcolor': INK, 'xtick.color': INK2,
                     'ytick.color': INK2, 'axes.grid': True, 'grid.color': GRID, 'grid.linewidth': 0.6,
                     'axes.spines.top': False, 'axes.spines.right': False, 'legend.frameon': False,
                     'figure.facecolor': '#fcfcfb', 'axes.facecolor': '#fcfcfb', 'lines.linewidth': 2})
OUT = 'organism/figures'
os.makedirs(OUT, exist_ok=True)
GROUPS = [('c12 pend', 'cap 12, end-of-PT start'), ('c6 pend', 'cap 6, end-of-PT start'), ('rfc pooled', 'cap 12, early starts (rfc)')]


def fig1():
    ex = json.load(open('artifacts/oa/q1_extra.json'))
    fig, ax = plt.subplots(1, 2, figsize=(9, 3.4))
    for j, (g, lab) in enumerate(GROUPS):
        d = ex['by_w1'][g]
        xs, ys, ns = [], [], []
        for k, (p, n) in d.items():
            lo, hi = [float(v) for v in k.split('..')]
            if n < 5:
                continue
            xs.append((max(lo, -40) + hi) / 2); ys.append(p); ns.append(n)
        ax[0].plot(xs, ys, '-o', color=COL[j], ms=5, label=lab)
        d = ex['by_term'][g]
        ks = [int(k) for k in d if d[k][1] >= 5]
        ax[1].plot(ks, [d[str(k)][0] for k in ks], '-o', color=COL[j], ms=5, label=lab)
    ax[0].set_xlabel('worst reference step log p at the start (nats, bin centre)')
    ax[0].set_ylabel('P(solved at r8)  [start-unsolved]')
    ax[1].set_xlabel('reference Lean term size (9 = 9 or more)')
    ax[1].set_xticks(range(1, 10))
    for a in ax:
        a.set_ylim(0, 1.05)
    ax[0].legend(loc='lower right')
    ax[0].set_title('worst step', color=INK, loc='left'); ax[1].set_title('proof size', color=INK, loc='left')
    fig.suptitle('Q1: what predicts "solved at r8" (best-cap12 / best-cap6, 9.56M, lean_staten; x0 reads)', color=INK, x=0.01, ha='left')
    fig.tight_layout(); fig.savefig(f'{OUT}/q1_predictors.png', dpi=150); plt.close(fig)


def fig2():
    S = [json.loads(l) for l in open('data/oa/q2_steps.jsonl')]
    H = [s for s in S if s['hard'] and s['run'] in ('c12', 'c6')]
    dn = lambda s: '( ¬ ( ¬' in s['action'].split(':=')[0]
    series = [('box:imp', '→I box', lambda s: s['cls'] == 'box:imp'),
              ('app', '→E / ¬E application', lambda s: s['cls'] == 'app'),
              ('and_proj', '∧E projection', lambda s: s['cls'] == 'and_proj'),
              ('or_intro', '∨I', lambda s: s['cls'] == 'or_intro'),
              ('box:orelim', '∨E box', lambda s: s['cls'] == 'box:orelim'),
              ('negO', '¬I box, other ¬X', lambda s: s['cls'] == 'box:neg' and not dn(s)),
              ('dneg', '¬I box proving ¬¬X', lambda s: s['cls'] == 'box:neg' and dn(s))]
    fig, ax = plt.subplots(1, 2, figsize=(11, 3.8), sharey=True)
    for a, run, title in ((ax[0], 'c12', 'best-cap12 (3 seeds)'), (ax[1], 'c6', 'best-cap6 (3 seeds)')):
        for j, (key, lab, f) in enumerate(series):
            g = [s for s in H if s['run'] == run and f(s)]
            med = [np.median([s['lp'][k] for s in g]) for k in range(9)]
            a.plot(range(9), med, '-o', ms=3.5, color=COL[j], label=f'{lab}')
        a.set_xticks(range(9)); a.set_xticklabels(['r0'] + [f'r{k}' for k in range(1, 9)])
        a.set_title(title, color=INK, loc='left'); a.set_xlabel('EI round (r0 = end of pretraining)')
    ax[0].set_ylabel('median log p of hard reference steps (nats)')
    ax[1].legend(loc='center left', bbox_to_anchor=(1.01, 0.5), fontsize=8)
    fig.suptitle('Q2: hard steps (log p < −4 at r0) of the shortest known proofs, by class (counts: artifacts/oa/q2_stdout.txt)', color=INK, x=0.01, ha='left')
    fig.tight_layout(); fig.savefig(f'{OUT}/q2_class_rounds.png', dpi=150); plt.close(fig)


def fig3():
    E = json.load(open('artifacts/oa/q3_entropy.json'))
    D = json.load(open('artifacts/oa/q3_div.json'))
    fig, ax = plt.subplots(1, 3, figsize=(11, 3.4))
    for j, run in enumerate(('c12', 'c6')):
        for s in (0, 1, 2):
            L = E['ladders'][f'{run} s{s}']
            ks = [p['k'] for p in L if p['H08'] is not None]
            ax[0].plot(ks, [p['H08'] for p in L if p['H08'] is not None], '-', color=COL[j], lw=1.2, alpha=0.9,
                       label=f'{"best-cap12" if run == "c12" else "best-cap6"}' if s == 0 else None)
            ks = [p['k'] for p in L if p['R_tr'] is not None]
            ax[1].plot(ks, [p['R_tr'] for p in L if p['R_tr'] is not None], '-', color=COL[j], lw=1.2)
            d = D[f'{run}|s{s}']['distinct_pruned_med_A']
            ax[2].plot(range(9), d, '-', color=COL[j], lw=1.2)
    ax[0].set_ylabel('on-policy token entropy, T 0.8 (nats)'); ax[0].set_title('policy entropy', color=INK, loc='left')
    ax[1].set_ylabel('EI training-sample accuracy'); ax[1].set_title('reward of samples from checkpoint', color=INK, loc='left')
    ax[2].set_ylabel('median distinct pruned proofs / A-theorem'); ax[2].set_title('diversity (x1 read, k 256)', color=INK, loc='left')
    for a in ax:
        a.set_xlabel('checkpoint (0 = end of pretraining)'); a.set_xticks(range(9))
    ax[0].legend(loc='upper right')
    fig.suptitle('Q3: entropy drops once (r0 → r1), then flat or slowly rising; reward and distinct proofs keep rising (one line per seed)',
                 color=INK, x=0.01, ha='left')
    fig.tight_layout(); fig.savefig(f'{OUT}/q3_entropy_diversity.png', dpi=150); plt.close(fig)


if __name__ == '__main__':
    for f in sys.argv[1:] or ['fig1', 'fig2', 'fig3']:
        globals()[f]()
