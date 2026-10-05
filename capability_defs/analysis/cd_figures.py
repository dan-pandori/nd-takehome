#!/usr/bin/env python3
"""capability-defs figures (static PNG, light surface; palette = the dataviz reference categorical slots 1-4, validated
with its validate_palette.js: all checks pass, aqua / yellow below 3:1 contrast -> every series is direct-labelled and
every figure has a table beside it in REPORT.md).

  python3 capability_defs/analysis/cd_figures.py   -> capability_defs/analysis/figures/*.png

F1 cd_kts.png        each RL-solved hard theorem's base k-to-solve interval [1/UB, 1/LB] (cap 12, r8, per seed), with the
                     budget lines k_eval / K_per / K_eval-set / K_total
F2 cd_elicit_curve.png  certified elicited / undetermined / certified created vs budget K (cap 12, r8, per seed)
F3 cd_agreement.png  agreement matrix (mean Jaccard over seeds) of the definitions' created sets (cap 12, r8, x0)
F4 cd_schema.png     key-step family shares per EI round (k 32 per round; round 1 = pend), per seed
"""
import json, math, os, sys
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'out')
FIG = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'figures')
SURF, INK, INK2, GRID = '#fcfcfb', '#0b0b0b', '#52514e', '#e4e3df'
C = ['#2a78d6', '#eb6834', '#1baf7a', '#eda100']       # categorical slots 1-4 (fixed order)
BLUES = ['#cde2fb', '#9ec5f4', '#6da7ec', '#3987e5', '#256abf', '#184f95', '#0d366b']
plt.rcParams.update({'figure.facecolor': SURF, 'axes.facecolor': SURF, 'savefig.facecolor': SURF, 'axes.edgecolor': GRID,
                     'axes.labelcolor': INK2, 'xtick.color': INK2, 'ytick.color': INK2, 'text.color': INK, 'font.size': 10,
                     'axes.spines.top': False, 'axes.spines.right': False, 'axes.grid': True, 'grid.color': GRID,
                     'grid.linewidth': 0.6})


def fig_kts(P, B):
    fig, axes = plt.subplots(1, 3, figsize=(13, 4.6), sharey=False)
    for s, ax in zip((0, 1, 2), axes):
        rows = B.get(str(s), {})
        H = [(n, r) for n, r in rows.items() if r['grp'] == 'H' and r.get('phat_r8', 0) > 0]
        if not H:
            ax.set_title(f'seed {s}: no data'); continue
        iv = []
        for n, r in H:
            lo_k = 1 / r['ub'] if r['ub'] > 0 else float('inf')                     # fewest attempts consistent with data
            hi_k = math.exp(-r['LB08']) if r['LB08'] > -math.inf else float('inf')    # most attempts (from the known-proof bound)
            iv.append((lo_k, hi_k, r['c'] > 0))
        iv.sort(key=lambda t: (t[1], t[0]))
        for i, (a, b, hit) in enumerate(iv):
            ax.plot([a, b], [i, i], color=C[0] if hit else C[1], lw=2, solid_capstyle='round')
        K = P['cov'].get(f's{s}_r8', {}).get('K_evalset')
        for k, lab in ((256, 'k_eval 256'), (K, 'K_eval-set'), (3.5e6, 'K_total')):
            if k:
                ax.axvline(k, color=INK2, lw=1, ls=(0, (3, 3)))
                ax.text(k, len(iv) + 0.5, lab, rotation=90, va='bottom', ha='right', fontsize=8, color=INK2)
        ax.set_xscale('log'); ax.set_xlim(1e2, 1e17)
        ax.set_title(f'seed {s} (cap 12): {len(iv)} RL-solved theorems pend fails 0 / 512', fontsize=10)
        ax.set_xlabel("pend's k-to-solve interval (attempts)")
        ax.set_yticks([])
    axes[0].plot([], [], color=C[0], lw=2, label='pend found a proof (J2 or earlier draws)')
    axes[0].plot([], [], color=C[1], lw=2, label='pend never succeeded')
    axes[0].legend(loc='lower right', frameon=False, fontsize=8)
    fig.suptitle("How many attempts would the base need? Each line is one theorem r8 solves: from the sampling bound (left)\n"
                 "to the known-proof likelihood bound (right). Budget lines: what RL's compute buys.", fontsize=10, x=0.01, ha='left')
    fig.tight_layout(rect=(0, 0, 1, 0.9)); fig.savefig(f'{FIG}/cd_kts.png', dpi=150); plt.close(fig)


def fig_curve(P):
    fig, axes = plt.subplots(1, 3, figsize=(13, 3.8), sharey=True)
    for s, ax in zip((0, 1, 2), axes):
        cur = P['curves'].get(f's{s}_r8')
        if not cur:
            continue
        K = [c[0] for c in cur]
        for j, (lab, col) in enumerate((('certified elicited', C[0]), ('certified created', C[2]), ('undetermined', C[1]))):
            y = [c[1 + j] for c in cur]
            ax.plot(K, y, color=col, lw=2)
            ax.text(K[-1] * 1.15, y[-1], lab, color=INK2, fontsize=8, va='center')
        ax.set_xscale('log'); ax.set_xlim(200, 1e8)
        ax.set_title(f'seed {s} (cap 12, r8)', fontsize=10); ax.set_xlabel('budget K (base attempts)')
    axes[0].set_ylabel('RL-solved hard theorems')
    fig.suptitle('The verdict depends on the budget: hard theorems r8 solves, classified at each budget K', fontsize=10, x=0.01, ha='left')
    fig.tight_layout(rect=(0, 0, 1, 0.92)); fig.savefig(f'{FIG}/cd_elicit_curve.png', dpi=150); plt.close(fig)


def fig_agree(P, defs, labels):
    M = np.array([[P['agree_r8'].get(f'{a}|{b}', float('nan')) for b in defs] for a in defs])
    fig, ax = plt.subplots(figsize=(7.2, 6))
    from matplotlib.colors import LinearSegmentedColormap
    cmap = LinearSegmentedColormap.from_list('blue', ['#f0efec'] + BLUES)
    im = ax.imshow(M, cmap=cmap, vmin=0, vmax=1)
    for i in range(len(defs)):
        for j in range(len(defs)):
            v = M[i, j]
            if not math.isnan(v):
                ax.text(j, i, f'{v:.2f}', ha='center', va='center', fontsize=7, color=SURF if v > 0.55 else INK)
    ax.set_xticks(range(len(defs))); ax.set_xticklabels(labels, rotation=55, ha='right', fontsize=8)
    ax.set_yticks(range(len(defs))); ax.set_yticklabels(labels, fontsize=8)
    ax.grid(False)
    cb = fig.colorbar(im, ax=ax, fraction=0.04); cb.set_label('Jaccard of created sets (mean over 3 seeds)', color=INK2)
    ax.set_title('Do the definitions agree on which theorems RL created? (cap 12, r8, draw x0)', fontsize=10, loc='left')
    fig.tight_layout(); fig.savefig(f'{FIG}/cd_agreement.png', dpi=150); plt.close(fig)


def fig_schema(S):
    fams = [('excluded_middle', 'excluded middle'), ('peirce', 'Peirce'), ('negated_conditional', 'negated conditional'),
            ('dist_and_over_or', 'distribution')]
    fig, axes = plt.subplots(1, 3, figsize=(13, 3.8), sharey=True)
    for s, ax in zip((0, 1, 2), axes):
        T = S['targets'][str(s)]
        for (f, lab), col in zip(fams, C):
            r = T[f]['rounds']; y = T[f]['share']
            ax.plot(r, y, color=col, lw=2)
            ax.text(r[-1] + 0.3, y[-1], lab, color=INK2, fontsize=8, va='center')
        ax.set_xlim(0.5, 20.5); ax.set_ylim(-0.03, 1.05)
        ax.set_title(f'seed {s} (cap 12)', fontsize=10); ax.set_xlabel('EI round (round 1 samples pend)')
    axes[0].set_ylabel('share of the family\'s targets\nsolved in that round (k 32)')
    fig.suptitle('Families acquired as a whole (members that need the key step only): each seed acquires different ones',
                 fontsize=10, x=0.01, ha='left')
    fig.tight_layout(rect=(0, 0, 1, 0.92)); fig.savefig(f'{FIG}/cd_schema.png', dpi=150); plt.close(fig)


def main():
    os.makedirs(FIG, exist_ok=True)
    P = json.load(open(f'{OUT}/part3.json'))
    B = json.load(open(f'{OUT}/bracket.json'))
    fig_kts(P, B)
    fig_curve(P)
    defs = ['eqk', 'cm', 'rel', 'tfmax', 'brk_ne', 'irt', 'schema', 'guided', 'sharp', 'npnt', 'ood']
    labels = ['equal-k 256', 'compute-matched', 'reliability', 'best known proof', 'bracket (not elic.)', 'IRT DIF',
              'schema family', 'guided too', 'expansion share', 'new proof+thm', 'rule-set novel']
    fig_agree(P, defs, labels)
    ks = f'{OUT}/schema_c12_keystep.json'
    if os.path.exists(ks):
        fig_schema(json.load(open(ks)))
    print('figures written to', FIG)


if __name__ == '__main__':
    main()
