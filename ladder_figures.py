#!/usr/bin/env python3
"""Figures for ladder-A from artifacts/ladder/summary.json (ladder_analysis.py output).
Palette: dataviz reference instance (categorical slots 1-6 for rungs T1-T6 in fixed order; frozen control = neutral grey dashed)."""
import json, os, sys, collections
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

CAT = {'T1': '#2a78d6', 'T2': '#eb6834', 'T3': '#1baf7a', 'T4': '#eda100', 'T5': '#e87ba4', 'T6': '#008300'}
GREY = '#9a9a96'; INK = '#0b0b0b'; INK2 = '#52514e'
LABEL = {'frozen': 'frozen control', 'T1': 'T1 EI', 'T2': 'T2 difficulty-weighted', 'T3': 'T3 relabelling', 'T4': 'T4 moving window', 'T5': 'T5 precursor injection', 'T6': 'T6 siblings'}
BINS = list(range(7, 15))


def _style(ax):
    for s in ('top', 'right'):
        ax.spines[s].set_visible(False)
    ax.grid(True, axis='y', color='#e6e5e1', linewidth=0.8); ax.set_axisbelow(True)
    ax.tick_params(colors=INK2, labelsize=9)


def solve_by_L(summ, pool, out):
    fig, ax = plt.subplots(figsize=(8, 4.4)); _style(ax)
    by_rung = collections.defaultdict(list)
    for arm, r in summ.items():
        by_rung[r['rung']].append(r)
    for rung in ['frozen'] + [f'T{i}' for i in range(1, 7)]:
        if rung not in by_rung:
            continue
        col = GREY if rung == 'frozen' else CAT[rung]
        for r in by_rung[rung]:
            ys = [100 * (r[pool]['bins'][str(L)]['rate'] or 0) for L in BINS]
            ax.plot(BINS, ys, color=col, linewidth=1.0, alpha=0.5, linestyle='--' if rung == 'frozen' else '-')
        mean = [100 * sum((r[pool]['bins'][str(L)]['rate'] or 0) for r in by_rung[rung]) / len(by_rung[rung]) for L in BINS]
        ax.plot(BINS, mean, color=col, linewidth=2, marker='o', markersize=6, linestyle='--' if rung == 'frozen' else '-', label=f"{LABEL[rung]} (n seeds = {len(by_rung[rung])})")
    ax.set_xlabel('true minimal length L_true (minlen.py, bound 14, restricted space)', color=INK2)
    ax.set_ylabel(f'{pool} theorems solved (%), 256 attempts', color=INK2)
    ax.set_xticks(BINS); ax.set_ylim(0, 100)
    ax.set_title(f'Solve rate by true length on the {pool} pool (thin: seeds; thick: mean)', color=INK, fontsize=11, loc='left')
    ax.legend(frameon=False, fontsize=8)
    fig.tight_layout(); fig.savefig(out, dpi=150); plt.close(fig)


def lstar(summ, out):
    fig, axes = plt.subplots(1, 2, figsize=(9, 3.8), sharey=True)
    rungs = ['frozen'] + [f'T{i}' for i in range(1, 7)]
    for ax, pool in zip(axes, ('transfer', 'targets')):
        _style(ax)
        fr = [r[pool]['lstar'] for r in summ.values() if r['rung'] == 'frozen']
        if fr:
            ax.axhline(max(fr), color=GREY, linestyle='--', linewidth=1.5, label='frozen control (max over seeds)')
        for i, rung in enumerate(rungs):
            rs = [r for r in summ.values() if r['rung'] == rung]
            for r in rs:
                dx = -0.12 if r['seed'] == '0' else 0.12
                ax.plot([i + dx], [r[pool]['lstar']], marker='o', markersize=8, color=GREY if rung == 'frozen' else CAT[rung], linestyle='none')
                ax.annotate(f"s{r['seed']}", (i + dx, r[pool]['lstar']), textcoords='offset points', xytext=(0, 7), ha='center', fontsize=7, color=INK2)
        ax.set_xticks(range(len(rungs))); ax.set_xticklabels(rungs)
        ax.set_title(f'L* on {pool} (≥ 5 theorems solved at L_true ≥ L)', color=INK, fontsize=10, loc='left')
        ax.set_ylim(6, 15)
    axes[0].set_ylabel('L*', color=INK2); axes[0].legend(frameon=False, fontsize=8)
    fig.tight_layout(); fig.savefig(out, dpi=150); plt.close(fig)


def reach(summ, out):
    fig, ax = plt.subplots(figsize=(8, 3.8)); _style(ax)
    arms = [a for a, r in summ.items() if r['transfer'].get('reachability') and r['rung'] != 'T6sib']
    xs = range(len(arms))
    el = [summ[a]['transfer']['reachability']['8']['elicit_1e-5'] for a in arms]
    sc = [summ[a]['transfer']['reachability']['8']['scored'] for a in arms]
    cr = [s - e for s, e in zip(sc, el)]
    ax.bar(xs, el, color='#86b6ef', width=0.6, label='elicitation (base p ≥ 1e-5)')
    ax.bar(xs, cr, bottom=el, color='#2a78d6', width=0.6, label='creation (base p < 1e-5)', edgecolor='white', linewidth=2)
    ax.set_xticks(list(xs)); ax.set_xticklabels([a.replace('la_', '') for a in arms], rotation=30, ha='right', fontsize=8)
    ax.set_ylabel('transfer theorems solved at L_true ≥ 8', color=INK2)
    ax.set_title('Base reachability of the solved transfer theorems beyond the frozen frontier', color=INK, fontsize=11, loc='left')
    ax.legend(frameon=False, fontsize=8)
    fig.tight_layout(); fig.savefig(out, dpi=150); plt.close(fig)


def counts(summ, out):
    """L* saturates at 10 for every trained rung, so the rungs are separated by how many transfer theorems they solve at the frontier."""
    fig, axes = plt.subplots(1, 2, figsize=(9, 3.8))
    rungs = [f'T{i}' for i in range(1, 7)]
    for ax, L in zip(axes, (9, 10)):
        _style(ax)
        t1 = [r['transfer']['ge'][str(L)] for r in summ.values() if r['rung'] == 'T1']
        if t1:
            ax.axhspan(min(t1), max(t1), color='#e6e5e1', alpha=0.7, linewidth=0, label='T1 seed range')
        for i, rung in enumerate(rungs):
            for r in [r for r in summ.values() if r['rung'] == rung]:
                dx = -0.12 if r['seed'] == '0' else 0.12
                v = r['transfer']['ge'][str(L)]
                ax.plot([i + dx], [v], marker='o', markersize=8, color=CAT[rung], linestyle='none', markeredgecolor='white', markeredgewidth=1)
                ax.annotate(f"s{r['seed']}{'' if r['rounds'] == 8 else ' (r' + str(r['rounds']) + ')'}", (i + dx, v), textcoords='offset points', xytext=(0, 8), ha='center', fontsize=7, color=INK2)
        ax.set_xticks(range(len(rungs))); ax.set_xticklabels(rungs); ax.set_xlim(-0.6, len(rungs) - 0.4)
        ax.set_title(f'Transfer theorems solved at L_true ≥ {L}', color=INK, fontsize=10, loc='left')
        ax.set_ylim(0, ax.get_ylim()[1] * 1.12)
    axes[0].set_ylabel('theorems solved (256 attempts each)', color=INK2); axes[0].legend(frameon=False, fontsize=8, loc='lower right')
    fig.text(0.01, 0.01, 'Frozen control at equal attempts: 0 at L_true ≥ 9 (both seeds). Two seeds per rung.', fontsize=8, color=INK2)
    fig.tight_layout(rect=(0, 0.04, 1, 1)); fig.savefig(out, dpi=150); plt.close(fig)


def main():
    summ = json.load(open(sys.argv[1] if len(sys.argv) > 1 else 'artifacts/ladder/summary.json'))
    os.makedirs('figures', exist_ok=True)
    solve_by_L(summ, 'transfer', 'figures/ladder_solve_transfer.png')
    solve_by_L(summ, 'targets', 'figures/ladder_solve_targets.png')
    lstar(summ, 'figures/ladder_lstar.png')
    counts(summ, 'figures/ladder_frontier_counts.png')
    if any(r['transfer'].get('reachability') for r in summ.values()):
        reach(summ, 'figures/ladder_reachability.png')
    print('figures written')


if __name__ == '__main__':
    main()
