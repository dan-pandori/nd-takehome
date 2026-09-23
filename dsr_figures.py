#!/usr/bin/env python3
"""Two figures for run ds-rendering, from artifacts/dsr/summary.json (dsr_analysis.py).

  figures/ds_rendering_lengths.png   distinct proofs written at 7 / 8 / >=9 ND lines, pass@16 on 1,638 transfer theorems
  figures/ds_rendering_readiness.png the readiness panel per arm beside the control

Colour rules (dataviz skill): identity is carried by the x-axis labels and the legend, never by colour alone -- the
arms are categories on the axis, so no categorical palette is needed.  Written ND length is an ORDINAL MAGNITUDE, so
it gets a single-hue sequential ramp (light -> dark, slot-1 blue), which is the one correct use of colour here.  The
control C0 is additionally hatched in every panel, so a reader in forced-colours or print still sees which bar is the
baseline.  No dual axes; values are direct-labelled; grid and axes are recessive.
"""
import json, os, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

S = json.load(open('artifacts/dsr/summary.json'))
ARMS = ['c0', 'r1', 'r3', 'r2']
LABEL = {'c0': 'C0\nlean_seq', 'r1': 'R1\nno premise\nre-statement', 'r3': 'R3\nformula-free\nhaves', 'r2': 'R2\nintro boxes'}
# single-hue sequential ramp off the reference palette's slot-1 blue (light -> dark = short -> long)
SEQ = ['#a8c9ee', '#5e9ae0', '#1c55a0']
INK, MUTED, SURF, GRID = '#0b0b0b', '#52514e', '#fcfcfb', '#e3e2dc'
plt.rcParams.update({'font.size': 8.5, 'axes.edgecolor': '#c9c8c2', 'axes.labelcolor': MUTED, 'xtick.color': MUTED,
                     'ytick.color': MUTED, 'text.color': INK, 'axes.spines.top': False, 'axes.spines.right': False,
                     'figure.facecolor': SURF, 'axes.facecolor': SURF, 'savefig.facecolor': SURF})


def get(arm, s, *path, default=None):
    v = S['arms'][arm]['seeds'][str(s)]
    for k in path:
        if v is None:
            return default
        v = v.get(k) if isinstance(v, dict) else None
    return default if v is None else v


def bars(ax, vals, title, ylab, fmt='{:.0f}', ref=None):
    """vals[arm] = [seed0, seed1]; one pair of bars per arm, direct-labelled, C0 hatched."""
    xs = []
    for i, arm in enumerate(ARMS):
        for j, v in enumerate(vals[arm]):
            x = i * 1.0 + (j - 0.5) * 0.34
            xs.append(x)
            if v is None:
                continue
            ax.bar(x, v, width=0.30, color=SEQ[1], edgecolor=SURF, linewidth=1.2,
                   hatch='//' if arm == 'c0' else None)
            ax.annotate(fmt.format(v), (x, v), textcoords='offset points', xytext=(0, 2), ha='center',
                        fontsize=7.2, color=INK)
    if ref is not None:
        ax.axhline(ref, color=MUTED, lw=1, ls=(0, (4, 2)))
    ax.set_xticks(range(len(ARMS)))
    ax.set_xticklabels([LABEL[a].replace('\n', ' ').split(' ')[0] for a in ARMS])
    ax.set_title(title, fontsize=8.5, color=INK, loc='left')
    ax.set_ylabel(ylab)
    ax.grid(axis='y', color=GRID, lw=0.8); ax.set_axisbelow(True)


def fig_lengths():
    fig, axes = plt.subplots(1, 3, figsize=(11.5, 3.5))
    for ax, key, name, col in zip(axes, ('d7', 'd8', 'd9plus'),
                                  ('7 ND lines', '8 ND lines', '≥ 9 ND lines'), SEQ):
        for i, arm in enumerate(ARMS):
            for j, s in enumerate((0, 1)):
                v = get(arm, s, 'mech_pass16', key)
                x = i + (j - 0.5) * 0.34
                if v is None:
                    continue
                ax.bar(x, v, width=0.30, color=col, edgecolor=SURF, linewidth=1.2,
                       hatch='//' if arm == 'c0' else None)
                ax.annotate(f'{v}', (x, v), textcoords='offset points', xytext=(0, 2), ha='center', fontsize=7.2)
        ax.set_xticks(range(len(ARMS))); ax.set_xticklabels([LABEL[a] for a in ARMS], fontsize=7.4)
        ax.set_title(name, fontsize=9, loc='left', color=INK)
        ax.grid(axis='y', color=GRID, lw=0.8); ax.set_axisbelow(True)
    axes[0].set_ylabel('distinct proofs (start-index-normalised)')
    fig.suptitle('Distinct proofs written at each ND length, pass@16 on 1,638 transfer theorems — two Stage-1 seeds per arm\n'
                 '3.2M from-scratch models, identical 155,000 ND records, batch 2048; hatched = control; Lean ∧ nd_verify',
                 fontsize=9, ha='left', x=0.007, y=1.0)
    fig.tight_layout(rect=[0, 0, 1, 0.86])
    os.makedirs('figures', exist_ok=True)
    fig.savefig('figures/ds_rendering_lengths.png', dpi=190)
    print('wrote figures/ds_rendering_lengths.png')


def fig_readiness():
    panels = [
        ('held', 'Held-out greedy (5,000)', lambda a, s: get(a, s, 'heldout_greedy', 'rate'), '{:.3f}', 'rate'),
        ('held6', 'Held-out greedy, 6-line bin (1,000)', lambda a, s: (lambda d: None if d is None else d.get('6'))(get(a, s, 'heldout_greedy', 'by_len')), '{:.3f}', 'rate'),
        ('d3', 'depth-3 base rate, pass@2,000 (1,000)', lambda a, s: get(a, s, 'cov', 'd3', 'rate'), '{:.3f}', 'targets hit / n'),
        ('d3req', 'depth-3 required@8, pass@2,000 (300)', lambda a, s: get(a, s, 'cov', 'd3req', 'rate'), '{:.3f}', 'targets hit / n'),
        ('red', 'required reductio, pass@2,000 (300)', lambda a, s: get(a, s, 'cov', 'red', 'targets_hit'), '{:.0f}', 'targets hit'),
        ('dial', 'dial EI − frozen, round 4 (1,000)', lambda a, s: (lambda e, f: None if e is None or f is None else e - f)(get(a, s, 'dial_ei', 'targets_cum_rate'), get(a, s, 'dial_frozen', 'targets_cum_rate')), '{:.3f}', 'Δ solved rate'),
        ('lafrz', 'ladder frozen, transfer solved (2,285)', lambda a, s: get(a, s, 'ladder_frozen', 'transfer_solved'), '{:.0f}', 'solved'),
        ('laT1', 'ladder T1, transfer solved (2,285)', lambda a, s: get(a, s, 'ladder_T1', 'transfer_solved'), '{:.0f}', 'solved'),
        ('lstar', 'ladder T1 L* (frozen L* labelled)', lambda a, s: get(a, s, 'ladder_T1', 'lstar'), '{:.0f}', 'L*'),
    ]
    fig, axes = plt.subplots(3, 3, figsize=(11.5, 9.0))
    for ax, (key, title, f, fmt, ylab) in zip(axes.ravel(), panels):
        vals = {a: [f(a, s) for s in (0, 1)] for a in ARMS}
        ref = None
        c0 = [v for v in vals['c0'] if v is not None]
        if c0:
            ref = sum(c0) / len(c0)
        bars(ax, vals, title, ylab, fmt=fmt, ref=ref)
    fig.suptitle('RL readiness per rendering, two Stage-1 seeds each — dashed line = the control C0 (mean of its two seeds)\n'
                 '3.2M from-scratch models on the identical 155,000-record cap-6 a1 set; sampler batch 2048; Lean ∧ nd_verify',
                 fontsize=9, ha='left', x=0.007, y=0.995)
    fig.tight_layout(rect=[0, 0, 1, 0.955])
    os.makedirs('figures', exist_ok=True)
    fig.savefig('figures/ds_rendering_readiness.png', dpi=175)
    print('wrote figures/ds_rendering_readiness.png')


if __name__ == '__main__':
    fig_lengths()
    fig_readiness()
