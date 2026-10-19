#!/usr/bin/env python3
"""Figures for run kalmar-pretrain, from kalmar/analysis.py's summary.json (VPS).

  python3 kalmar/figures.py [--summary artifacts/kalmar/summary.json] [--out figures/kalmar_pretrain.png]

Four panels: (a) teacher-forced agreement by step type; (b) greedy free generation by atom count (Lean-valid and
exact-follow); (c) plain pass@32 by the algorithm's proof length; (d) KAL-D learning curve over training steps.
Colours: the dataviz reference palette's first three categorical slots (validated all-pairs, light surface);
every series is direct-labelled because the third slot is below 3:1 contrast.
"""
import argparse, json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

COL = {'KAL-D': '#2a78d6', 'KAL-C': '#eb6834', 'control': '#1baf7a'}
INK, MUTED, GRID = '#1f1f1f', '#6b6b6b', '#e6e6e4'
STEPS = [('tagg=pr', 'premise line'), ('tagg=lem', 'X ∨ ¬X derivation'), ('tagg=split', 'split (∨E)'),
         ('tagg=efq', 'ex falso'), ('tagg=leaf:and+', 'leaf ∧ true'), ('tagg=leaf:and-', 'leaf ∧ false'),
         ('tagg=leaf:or+', 'leaf ∨ true'), ('tagg=leaf:or-', 'leaf ∨ false'), ('tagg=leaf:imp+B', 'leaf → (B true)'),
         ('tagg=leaf:imp+A', 'leaf → (A false)'), ('tagg=leaf:imp-', 'leaf → false'), ('tagg=leaf:not+', 'leaf ¬¬A'),
         ('tagg=leaf:bot-', 'leaf ¬⊥'), ('tagg=close', 'box close'), ('all', 'ALL STATES')]


def style(ax):
    for s in ('top', 'right'):
        ax.spines[s].set_visible(False)
    for s in ('left', 'bottom'):
        ax.spines[s].set_color(MUTED)
    ax.tick_params(colors=MUTED, labelcolor=INK, labelsize=8)
    ax.grid(True, color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)


def mean(xs):
    xs = [x for x in xs if x is not None]
    return sum(xs) / len(xs) if xs else None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--summary', default='artifacts/kalmar/summary.json')
    ap.add_argument('--out', default='figures/kalmar_pretrain.png')
    a = ap.parse_args()
    S = json.load(open(a.summary))
    fig, axs = plt.subplots(2, 2, figsize=(12, 9.5))
    # (a) TF agreement by step type
    ax = axs[0][0]
    arms = [x for x in ('KAL-D', 'KAL-C', 'control') if x in S.get('tf', {})]
    for j, arm in enumerate(arms):
        for i, (key, lab) in enumerate(STEPS):
            vals = [v for v in S['tf'][arm].get(key, []) if v is not None]
            if not vals:
                continue
            y = len(STEPS) - 1 - i + (j - 1) * 0.22
            ax.plot([100 * min(vals), 100 * max(vals)], [y, y], color=COL[arm], linewidth=2, solid_capstyle='round')
            ax.plot(100 * mean(vals), y, 'o', color=COL[arm], markersize=6, markeredgecolor='white', markeredgewidth=1,
                    label=arm if i == 0 else None)
    ax.set_yticks(range(len(STEPS)))
    ax.set_yticklabels([lab for _, lab in reversed(STEPS)])
    ax.set_xlim(-2, 102)
    ax.set_xlabel('greedy action = the algorithm\'s (% of states; dot = seed mean, bar = seed range)', color=INK, fontsize=8)
    ax.set_title('(a) Teacher-forced agreement with Kalmár, 1,200 held-out theorems', color=INK, fontsize=10, loc='left')
    ax.legend(frameon=False, fontsize=8, loc='lower left')
    style(ax)
    # (b) greedy free generation by atoms
    ax = axs[0][1]
    for arm in arms:
        fr = S.get('free', {}).get(arm)
        if not fr:
            continue
        xs = [1, 2, 3, 4]
        v = [mean(fr[f'atoms={k}']['valid']) for k in xs]
        f = [mean(fr[f'atoms={k}']['follow']) for k in xs]
        ax.plot(xs, [100 * x for x in v], '-o', color=COL[arm], linewidth=2, markersize=8, markeredgecolor='white')
        ax.plot(xs, [100 * x for x in f], '--o', color=COL[arm], linewidth=2, markersize=8, markeredgecolor=COL[arm],
                markerfacecolor='white', markeredgewidth=2)
        ax.annotate(f'{arm} valid', (4, 100 * v[-1]), xytext=(6, 0), textcoords='offset points', color=INK, fontsize=8,
                    va='center')
        if arm != 'control':
            ax.annotate(f'{arm} exact Kalmár', (4, 100 * f[-1]), xytext=(6, -2), textcoords='offset points', color=MUTED,
                        fontsize=8, va='center')
    ax.set_xticks([1, 2, 3, 4])
    ax.set_xlim(0.8, 5.4)
    ax.set_ylim(-3, 103)
    ax.set_xlabel('atoms in the theorem', color=INK, fontsize=8)
    ax.set_ylabel('% of theorems (greedy, Lean)', color=INK, fontsize=8)
    ax.set_title('(b) Greedy proofs: valid (solid) and exactly the algorithm\'s (dashed)', color=INK, fontsize=10, loc='left')
    style(ax)
    # (c) plain pass@32 by algorithm proof length
    ax = axs[1][0]
    bins = ['0-99', '100-149', '150-199', '200-299', '300-1024']
    for arm in arms:
        bd = S.get('breakdown', {}).get(arm, {}).get('algo_len')
        if not bd:
            continue
        xs = [i for i, b in enumerate(bins) if b in bd]
        ys = [100 * mean(bd[bins[i]]) for i in xs]
        ax.plot(xs, ys, '-o', color=COL[arm], linewidth=2, markersize=8, markeredgecolor='white')
        ax.annotate(arm, (xs[-1], ys[-1]), xytext=(6, 0), textcoords='offset points', color=INK, fontsize=8, va='center')
    ax.set_xticks(range(len(bins)))
    ax.set_xticklabels(bins)
    ax.set_xlim(-0.3, len(bins) - 0.3)
    ax.set_ylim(-3, 103)
    ax.set_xlabel('length of the algorithm\'s proof (state-env actions)', color=INK, fontsize=8)
    ax.set_ylabel('plain pass@32 (%)', color=INK, fontsize=8)
    ax.set_title('(c) Solve rate vs Kalmár proof length (standard sets pooled)', color=INK, fontsize=10, loc='left')
    style(ax)
    # (d) learning curve
    ax = axs[1][1]
    cv = S.get('curve', {})
    pts = sorted((int(k), v) for k, v in cv.items())
    for s in range(3):
        xs = [k for k, v in pts if v['tf'][s] is not None]
        ys = [100 * v['tf'][s] for k, v in pts if v['tf'][s] is not None]
        if xs:
            ax.plot(xs, ys, '-o', color=COL['KAL-D'], linewidth=2, markersize=6, markeredgecolor='white', alpha=0.9)
        xs2 = [k for k, v in pts if v['greedy_valid'][s] is not None]
        ys2 = [100 * v['greedy_valid'][s] for k, v in pts if v['greedy_valid'][s] is not None]
        if xs2:
            ax.plot(xs2, ys2, '--o', color=COL['KAL-D'], linewidth=2, markersize=6, markeredgecolor=COL['KAL-D'],
                    markerfacecolor='white', markeredgewidth=2, alpha=0.9)
    kc = S.get('tf', {}).get('KAL-C', {}).get('all')
    if kc:
        ax.plot([24020], [100 * mean(kc)], 's', color=COL['KAL-C'], markersize=8, markeredgecolor='white')
        ax.annotate('KAL-C (own schedule)', (24020, 100 * mean(kc)), xytext=(8, -10), textcoords='offset points',
                    color=INK, fontsize=8)
    ax.set_xscale('log')
    ax.set_ylim(-3, 103)
    ax.set_xlabel('KAL-D training step (log; snapshots are mid-schedule)', color=INK, fontsize=8)
    ax.set_ylabel('%', color=INK, fontsize=8)
    ax.set_title('(d) KAL-D: TF agreement (solid), greedy valid (dashed), per seed', color=INK, fontsize=10, loc='left')
    style(ax)
    fig.tight_layout()
    fig.savefig(a.out, dpi=150, facecolor='#fcfcfb')
    print('wrote', a.out)


if __name__ == '__main__':
    main()
