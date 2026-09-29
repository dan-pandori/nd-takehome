#!/usr/bin/env python3
"""state-cap12 figure: generator-only solve rate per `L_true` bin on long-pool's rr600 (+ the >= 17 file), final
checkpoints, k 256.  Left: T1; right: frozen (Stage-1).  Thin lines = seeds, thick = arm mean.
  python3 sc12_figure.py --summary artifacts/sc12/summary.json --out figures/state_cap12.png
"""
import argparse, json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

SURF, INK, INK2 = '#fcfcfb', '#0b0b0b', '#52514e'
# reference palette slots 1-3 (blue, orange, aqua), fixed per entity; marker + dash as a second cue
STY = {'SN-v2 cap 6': ('#2a78d6', 'o', '-'), 'K12 whole-proof': ('#eb6834', 's', '--'), 'SN cap 12': ('#1baf7a', 'D', '-')}
PANELS = [('T1 (8 EI rounds, final checkpoint)', {'SN-v2 cap 6': 'SN-v2 cap-6 T1', 'K12 whole-proof': 'K12 T1 (whole-proof)',
                                                  'SN cap 12': 'SN-cap12 T1'}),
          ('frozen (Stage-1 only)', {'SN-v2 cap 6': 'SN-v2 cap-6 frozen', 'K12 whole-proof': 'K12 frozen (whole-proof)',
                                    'SN cap 12': 'SN-cap12 frozen'})]
BINS = list(range(11, 17))


def rates(o):
    r = [100 * o['gen_by_bin'][str(L)] / o['gen_n'][str(L)] for L in BINS]
    return r + [100 * (o['ge17'] or 0) / 70]


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--summary', default='artifacts/sc12/summary.json')
    ap.add_argument('--out', default='figures/state_cap12.png'); a = ap.parse_args()
    S = json.load(open(a.summary))
    fig, axs = plt.subplots(1, 2, figsize=(11, 4.2), sharey=True, facecolor=SURF)
    xs = list(range(len(BINS) + 1)); xl = [str(L) for L in BINS] + ['≥17']
    for ax, (title, arms) in zip(axs, PANELS):
        ax.set_facecolor(SURF)
        for lab, arm in arms.items():
            cells = {k: v for k, v in S.get(arm, {}).items() if not k.startswith('_')}
            if not cells:
                continue
            c, m, ls = STY[lab]; R = [rates(o) for o in cells.values()]
            for r in R:
                ax.plot(xs, r, color=c, lw=0.8, alpha=0.35, ls=ls)
            mean = [sum(col) / len(col) for col in zip(*R)]
            ax.plot(xs, mean, color=c, lw=2, ls=ls, marker=m, ms=8, mec=SURF, mew=2, label=f'{lab} (n = {len(R)})')
        ax.set_title(title, color=INK, fontsize=11, loc='left')
        ax.set_xticks(xs); ax.set_xticklabels(xl, color=INK2); ax.set_xlabel('L_true bin (ND-derived; upper bound under Lean)', color=INK2)
        ax.grid(axis='y', color='#e6e5e0', lw=0.8); ax.set_axisbelow(True)
        for s in ('top', 'right'):
            ax.spines[s].set_visible(False)
        for s in ('left', 'bottom'):
            ax.spines[s].set_color('#b5b4ad')
        ax.tick_params(colors=INK2)
    axs[0].set_ylabel('generator theorems solved (%)', color=INK2)
    axs[0].legend(frameon=False, fontsize=9, labelcolor=INK)
    axs[1].legend(frameon=False, fontsize=9, labelcolor=INK)
    fig.suptitle('Long pool (rr600 generator theorems + ≥17 file), k 256, Lean alone. Thin: seeds; thick: mean',
                 color=INK, fontsize=10, x=0.01, ha='left')
    fig.tight_layout(); fig.savefig(a.out, dpi=150, facecolor=SURF); print(a.out)


if __name__ == '__main__':
    main()
