#!/usr/bin/env python3
"""support-curves figures: the per-theorem support scatter and the per-stratum pass@k curves.

  python3 sc_figures.py --summary artifacts/sc/summary.json --report artifacts/sc/report.json \
      --out figures/support_curves

Colour follows the `dataviz` skill's rules.  `L_true` is an ORDERED magnitude, so the scatter uses the
reference palette's SEQUENTIAL blue ramp (one hue, light -> dark), not a categorical set.  The pass@k panels
compare two entities, so they use categorical slots 1 and 2 (blue #2a78d6, orange #eb6834); `references/palette.md`
documents the first three slots as passing the all-pairs gates in both modes, and a two-member subset of a
validated set cannot have a worse worst-pair, so that pair is validated by the palette document.  (The
validator script itself is node, which this VPS does not have.)  No dual axis anywhere; legends always
present; grid and axes recessive; text in ink, never in a series colour.
"""
import argparse, json, math, os, collections
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

SEQ = ['#cde2fb', '#9ec5f4', '#6da7ec', '#3987e5', '#2a78d6', '#1c5cab', '#184f95', '#0d366b']  # blue 100..650
BASE_C, EI_C = '#2a78d6', '#eb6834'          # categorical slots 1, 2
INK, INK2, GRID = '#1a1a1a', '#555555', '#d8d8d8'
EI_ATTEMPTS = 8 * 32                          # the attempts expert iteration itself spent per target


def style(ax):
    ax.set_facecolor('white')
    for s in ('top', 'right'):
        ax.spines[s].set_visible(False)
    for s in ('left', 'bottom'):
        ax.spines[s].set_color(GRID)
    ax.tick_params(colors=INK2, labelsize=8, length=3)
    ax.grid(True, color=GRID, lw=0.6, alpha=0.7)
    ax.set_axisbelow(True)


def scatter(cells, out, seed=0, T=0.8):
    base = {c['name']: c for c in cells if c['model'] == 'base' and c['seed'] == seed and c['temperature'] == T}
    ei = {c['name']: c for c in cells if c['model'] == 'ei' and c['seed'] == seed and c['temperature'] == T}
    names = sorted(set(base) & set(ei))
    Ls = sorted({base[n]['L_true'] for n in names})
    cmap = {L: SEQ[min(i, len(SEQ) - 1)] for i, L in enumerate(Ls)}
    fig, ax = plt.subplots(figsize=(7.2, 6.0), dpi=160)
    style(ax)
    n_bb = n_bx = n_by = n_xy = 0
    for n in names:
        b, e = base[n], ei[n]
        bx, b0 = (math.log10(b['p_hat']), False) if b['c'] else (math.log10(3.0 / b['n']), True)
        ey, e0 = (math.log10(e['p_hat']), False) if e['c'] else (math.log10(3.0 / e['n']), True)
        col = cmap[b['L_true']]
        if b0 and e0:
            n_xy += 1
            continue                      # neither model ever solved it: no information for this plot
        ax.plot([bx], [ey], 'o', ms=5.0, color=col, mec='white', mew=0.7, zorder=3)
        if b0:                            # p_base is an upper bound: arrow pointing left
            n_bx += 1
            ax.annotate('', xy=(bx - 0.42, ey), xytext=(bx, ey), zorder=2,
                        arrowprops=dict(arrowstyle='-|>', color=col, lw=1.1, shrinkA=2, shrinkB=0))
        if e0:
            n_by += 1
            ax.annotate('', xy=(bx, ey - 0.42), xytext=(bx, ey), zorder=2,
                        arrowprops=dict(arrowstyle='-|>', color=col, lw=1.1, shrinkA=2, shrinkB=0))
        if not b0 and not e0:
            n_bb += 1
    lo = min(ax.get_xlim()[0], ax.get_ylim()[0]); hi = max(ax.get_xlim()[1], ax.get_ylim()[1])
    ax.plot([lo, hi], [lo, hi], '-', color=INK2, lw=1.0, alpha=0.55, zorder=1)
    ax.text(hi - 0.35, hi - 0.55, 'equal', color=INK2, fontsize=8, ha='right', va='bottom', rotation=45)
    ax.axvline(math.log10(1.0 / EI_ATTEMPTS), color=INK2, lw=1.0, ls=(0, (4, 3)), alpha=0.8, zorder=1)
    ax.text(math.log10(1.0 / EI_ATTEMPTS) - 0.10, lo + 0.25, f'p_base = 1/{EI_ATTEMPTS}\n(the attempts EI spent)',
            color=INK2, fontsize=7.5, va='bottom', ha='right')
    ax.set_xlim(lo, hi); ax.set_ylim(lo, hi)
    ax.set_xlabel('log$_{10}$  base per-sample success probability', color=INK, fontsize=9.5)
    ax.set_ylabel('log$_{10}$  EI per-sample success probability', color=INK, fontsize=9.5)
    ax.set_title(f'Per-theorem support, seed {seed}, T = {T}  ({len(names) - n_xy} of {len(names)} theorems solved by '
                 f'at least one model)', color=INK, fontsize=10.5, pad=10)
    h = [Line2D([], [], marker='o', ls='', ms=5.5, mec='white', mew=0.7, color=cmap[L], label=f'{L}') for L in Ls]
    h.append(Line2D([], [], marker='>', ls='', ms=5, color=INK2, label='0 successes:\n95 % upper bound'))
    lg = ax.legend(handles=h, title='$L_{true}$ (ND upper bound)', loc='lower right', fontsize=7.5,
                   title_fontsize=8, frameon=True, framealpha=0.95, edgecolor=GRID, ncol=2)
    lg.get_title().set_color(INK)
    for t in lg.get_texts():
        t.set_color(INK)
    fig.text(0.01, 0.01, f'{n_bb} both solved  |  {n_bx} base 0 (arrow left)  |  {n_by} EI 0 (arrow down)  |  '
                         f'{n_xy} neither, omitted', color=INK2, fontsize=7.5)
    fig.tight_layout(rect=(0, 0.025, 1, 1))
    fig.savefig(out + '_scatter.png', facecolor='white')
    print(f'-> {out}_scatter.png  ({n_bb} both, {n_bx} base-0, {n_by} ei-0, {n_xy} neither)')
    plt.close(fig)


def passk(report, out, seed=0, T=0.8):
    st = [v for v in report['strata'].values() if v['seed'] == seed and v['temperature'] == T and v['curve']]
    st.sort(key=lambda v: v['L_true'])
    if not st:
        print('no strata to plot'); return
    ncol = min(4, len(st)); nrow = (len(st) + ncol - 1) // ncol
    fig, axes = plt.subplots(nrow, ncol, figsize=(3.0 * ncol, 2.7 * nrow), dpi=160, squeeze=False)
    for i, v in enumerate(st):
        ax = axes[i // ncol][i % ncol]
        style(ax)
        # json.load turns the integer k keys into STRINGS; sorting those lexicographically gives
        # 1, 10, 100, 1000, 10000, 2000, 256, ... and draws a zig-zag instead of a monotone pass@k curve.
        cv = {int(k): val for k, val in v['curve'].items()}
        ks = sorted(cv)
        kx = [k for k in ks if cv[k]['exact']]
        for col, key in ((BASE_C, 'base'), (EI_C, 'ei')):
            ax.plot(ks, [cv[k][key] for k in ks], '--', color=col, lw=1.6, alpha=0.85)   # plug-in tail
            if kx:
                ax.plot(kx, [cv[k][key] for k in kx], '-o', color=col, lw=2.2, ms=4)     # exact estimator
        if kx and max(kx) < max(ks):
            ax.axvline(max(kx), color=GRID, lw=1.0)
        ax.set_xscale('log'); ax.set_ylim(-0.03, 1.03)
        ax.set_title(f'$L_{{true}}$ = {v["L_true"]}  ({v["n_theorems"]} thms)', color=INK, fontsize=9)
        if v['crossover_k']:
            ax.axvline(v['crossover_k'], color=INK2, lw=1.0, ls=(0, (4, 3)))
            ax.text(v['crossover_k'], 1.0, f'  crossover\n  k={v["crossover_k"]:,}', color=INK2, fontsize=7, va='top')
        if i % ncol == 0:
            ax.set_ylabel('pass@k', color=INK, fontsize=9)
        if i // ncol == nrow - 1:
            ax.set_xlabel('k (attempts)', color=INK, fontsize=9)
    for j in range(len(st), nrow * ncol):
        axes[j // ncol][j % ncol].axis('off')
    h = [Line2D([], [], color=BASE_C, lw=2.2, label='base (Stage 1 only)'),
         Line2D([], [], color=EI_C, lw=2.2, label='EI (8 rounds x k 32)'),
         Line2D([], [], color=INK2, lw=1.6, ls='--', label='dashed: binomial plug-in past the attempts drawn')]
    lg = fig.legend(handles=h, loc='lower center', ncol=3, fontsize=8.5, frameon=False)
    for t in lg.get_texts():
        t.set_color(INK)
    fig.suptitle(f'pass@k by true minimal length, seed {seed}, T = {T}  (solid = unbiased estimator; '
                 f'dashed = plug-in past the attempts drawn)', color=INK, fontsize=10.5)
    fig.tight_layout(rect=(0, 0.055, 1, 0.955))
    fig.savefig(out + '_passk.png', facecolor='white')
    print(f'-> {out}_passk.png  ({len(st)} strata)')
    plt.close(fig)


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--summary', default='artifacts/sc/summary.json')
    ap.add_argument('--report', default='artifacts/sc/report.json')
    ap.add_argument('--out', default='figures/support_curves')
    ap.add_argument('--seed', type=int, default=0)
    ap.add_argument('--temperature', type=float, default=0.8)
    a = ap.parse_args()
    os.makedirs(os.path.dirname(a.out) or '.', exist_ok=True)
    scatter(json.load(open(a.summary)), a.out, a.seed, a.temperature)
    if os.path.exists(a.report):
        passk(json.load(open(a.report)), a.out, a.seed, a.temperature)
