#!/usr/bin/env python3
"""The run's figure (style-edl): EDL per proof by stream, each learner seed marked, with pass@32 after training.

  python3 style_edl/figure.py [--csv style_edl/results.csv] [--out figures/style_edl.png]

Left: the brief's EDL (hollow) and EDL_c (filled) per proof, bits, symlog axis (linear within ±1 bit); streams in the
order of the learner's teacher-forced disagreement with them (style distance). The grey band is the pre-registered
floor ±F. Middle: the cross-fitted EDL (exploratory; stream and test halves swapped and averaged). Right: plain pass@32
and pass@1 on the 128 test theorems after training (θ*), the learner's values as dashed lines.
Colours: the reference categorical palette's first three slots in fixed order (seed 0 / 1 / 2), each seed also its own
marker shape, so identity is never colour alone.
"""
import argparse, csv, os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SEED_C = ('#2a78d6', '#eb6834', '#1baf7a')
SEED_M = ('o', 's', '^')
INK, INK2, GRID = '#0b0b0b', '#52514e', '#e4e3df'
NAMES = {'S_own': 'S_own', 'S_own2': 'S_own2', 'S_seed': 'S_seed', 'S_short': 'S_short', 'S_RL': 'S_RL', 'S_Kal': 'S_Kalmár'}


def f(x):
    return float(x) if x not in (None, '') else None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--csv', default='style_edl/results.csv')
    ap.add_argument('--floor', type=float, default=0.1)
    ap.add_argument('--out', default='figures/style_edl.png')
    a = ap.parse_args()
    rows = list(csv.DictReader(open(os.path.join(ROOT, a.csv))))
    streams = []
    for r in rows:
        if r['stream'] not in streams:
            streams.append(r['stream'])
    dist = {S: sum(1 - f(r['tf_agree']) for r in rows if r['stream'] == S) / 3 for S in streams}
    streams.sort(key=lambda S: dist[S])
    x = {S: i for i, S in enumerate(streams)}
    plt.rcParams.update({'font.size': 9, 'axes.edgecolor': INK2, 'axes.labelcolor': INK, 'xtick.color': INK2,
                         'ytick.color': INK2, 'axes.spines.top': False, 'axes.spines.right': False})
    fig, ax = plt.subplots(1, 3, figsize=(13.5, 4.6), gridspec_kw={'width_ratios': [1.2, 1.2, 1.0]})
    off = (-0.18, 0.0, 0.18)
    for k, (key, hollow, lab) in enumerate((('EDL_pp', True, "EDL (brief's)"), ('EDL_c_pp', False, 'EDL_c (split-corrected)'))):
        for r in rows:
            s = int(r['seed']); v = f(r[key])
            if v is None:
                continue
            ax[0].plot(x[r['stream']] + off[s] + (0.05 if hollow else -0.05), v, SEED_M[s], ms=7,
                       mfc='none' if hollow else SEED_C[s], mec=SEED_C[s], mew=1.6, zorder=3)
    for r in rows:
        s = int(r['seed'])
        for key, hollow in (('xfit_EDL_pp', False), ('lv_EDL_c_pp', True)):
            v = f(r.get(key))
            if v is not None:
                ax[1].plot(x[r['stream']] + off[s] + (0.05 if hollow else -0.05), v, SEED_M[s], ms=7,
                           mfc='none' if hollow else SEED_C[s], mec=SEED_C[s], mew=1.6, zorder=3)
    K = ('EDL_pp', 'EDL_c_pp', 'xfit_EDL_pp', 'lv_EDL_c_pp')
    lo = min([f(r[k]) for r in rows for k in K if f(r.get(k)) is not None] + [-1])
    hi = max([f(r[k]) for r in rows for k in K if f(r.get(k)) is not None] + [1])
    ticks = [t for t in (-100, -10, -5, -1, -0.5, 0, 0.5, 1, 10, 100, 1000) if lo * 1.5 <= t <= hi * 1.5]
    for i in (0, 1):
        ax[i].set_yscale('symlog', linthresh=1.0, linscale=1.5)
        ax[i].set_ylim(min(lo * 1.6, -1.2), hi * 1.6)
        ax[i].set_yticks(ticks)
        ax[i].set_yticklabels([f'{t:g}' for t in ticks])
        ax[i].axhspan(-a.floor, a.floor, color=GRID, zorder=0, lw=0)
        ax[i].axhline(0, color=INK2, lw=0.8, zorder=1)
        ax[i].set_ylabel('bits per proof')
        ax[i].grid(axis='y', color=GRID, lw=0.6)
    ax[0].set_title('EDL per proof (hollow: EDL, filled: EDL_c)', fontsize=9.5, color=INK, loc='left')
    ax[1].set_title('filled: cross-fitted EDL (exploratory); hollow: ℓ_V EDL_c', fontsize=9.5, color=INK, loc='left')
    for r in rows:
        s = int(r['seed'])
        for key, hollow in (('plain_pass32_after', False), ('plain_pass1_after', True)):
            v = f(r.get(key))
            if v is not None:
                ax[2].plot(x[r['stream']] + off[s], v, SEED_M[s], ms=7, mfc='none' if hollow else SEED_C[s],
                           mec=SEED_C[s], mew=1.6, zorder=3)
    for s in (0, 1, 2):
        for key, ls in (('plain_pass32_before', '--'), ('plain_pass1_before', ':')):
            vs = [f(r.get(key)) for r in rows if int(r['seed']) == s and f(r.get(key)) is not None]
            if vs:
                ax[2].axhline(vs[0], color=SEED_C[s], lw=0.9, ls=ls, zorder=1)
    ax[2].set_ylim(0.0, 1.03)
    ax[2].set_ylabel('plain, T 0.8, k 32, test theorems')
    ax[2].set_title('after training: pass@32 (filled), pass@1 (hollow)', fontsize=9.5, color=INK, loc='left')
    ax[2].set_yticks([0, 0.2, 0.4, 0.6, 0.8, 0.9, 1.0])
    ax[2].grid(axis='y', color=GRID, lw=0.6)
    for i in range(3):
        ax[i].set_xticks(range(len(streams)))
        ax[i].set_xticklabels([NAMES.get(S, S) for S in streams], rotation=30, ha='right')
        ax[i].set_xlim(-0.6, len(streams) - 0.4)
    hs = [plt.Line2D([], [], ls='none', marker=SEED_M[s], ms=7, color=SEED_C[s], label=f'learner seed {s}') for s in (0, 1, 2)]
    fig.legend(handles=hs, loc='upper center', ncol=3, frameon=False, bbox_to_anchor=(0.5, 1.0))
    fig.text(0.01, 0.01, 'Streams ordered by the learner\'s teacher-forced disagreement with them (style distance). Grey band: '
             f'the pre-registered floor ±{a.floor:g} bits per proof; axes linear within ±1 bit, logarithmic beyond.\n'
             'Learners: best-state stage1_best12_s0–s2 (9.56 M params, lean_staten, from scratch on K12). A_ES fine-tuning, '
             'lr chosen by prequential code. ℓ_V: any collected valid proof counts. Right: dashed / dotted = learner pass@32 / pass@1.',
             fontsize=7.5, color=INK2)
    fig.tight_layout(rect=(0, 0.07, 1, 0.93))
    os.makedirs(os.path.dirname(os.path.join(ROOT, a.out)), exist_ok=True)
    fig.savefig(os.path.join(ROOT, a.out), dpi=150, facecolor='#fcfcfb')
    print('wrote', a.out)


if __name__ == '__main__':
    main()
