#!/usr/bin/env python3
"""Figures for run proof-strategies (static PNG, light mode; palette = the dataviz skill's validated categorical slots
1-3, checked with its validator: blue #2a78d6, orange #eb6834, aqua #1baf7a; text and chrome in ink / muted grays).
Every value plotted is read from artifacts/ps/summary/*.json and the label files; TABLES.md holds the same numbers.

  python3 proof_strategies/figures.py      # -> proof_strategies/figures/*.png
"""
import gzip, json, os, sys
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from strategies import STRATS, NAME                       # noqa: E402

BLUE, ORANGE, AQUA = '#2a78d6', '#eb6834', '#1baf7a'
SURF, INK, INK2, MUTED, GRID, AXIS = '#fcfcfb', '#0b0b0b', '#52514e', '#898781', '#e1e0d9', '#c3c2b7'
IDLE = '#b9b8b1'
WORK = {'cond_proof': 'cond_proof.working', 'cases': 'cases.genuine', 'neg_intro': 'neg_intro.working', 'contradiction': 'contradiction.working'}
OUT = os.path.join(HERE, 'figures')
plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 10, 'axes.edgecolor': AXIS, 'axes.labelcolor': INK2,
                     'xtick.color': INK2, 'ytick.color': INK, 'text.color': INK, 'figure.facecolor': SURF, 'axes.facecolor': SURF})


def summ(name):
    return json.load(open(f'artifacts/ps/summary/{name}.json'))


def style(ax):
    for sp in ('top', 'right', 'left'):
        ax.spines[sp].set_visible(False)
    ax.spines['bottom'].set_color(AXIS)
    ax.tick_params(axis='y', length=0)
    ax.grid(axis='x', color=GRID, linewidth=1)
    ax.set_axisbelow(True)


def fig_mix():
    k = summ('k12'); n = k['n']
    rows = []
    for s in STRATS:
        u = 100 * k['uses'][s] / n
        w = 100 * k['sub'][WORK[s]] / n if s in WORK else u
        rows.append((NAME[s], u, w))
    rows.sort(key=lambda r: r[1])
    fig, ax = plt.subplots(figsize=(8.2, 5.4))
    y = range(len(rows))
    ax.barh(y, [r[2] for r in rows], height=0.62, color=BLUE, edgecolor=SURF, linewidth=2,
            label='at least one instance does logical work (or the strategy has no idle test)')
    ax.barh(y, [r[1] - r[2] for r in rows], left=[r[2] for r in rows], height=0.62, color=IDLE, edgecolor=SURF, linewidth=2,
            label='every instance idle (assumption unused, redundant split, template reductio)')
    for i, r in enumerate(rows):
        lab = f'{r[1]:.2f} %' if r[1] < 1 else f'{r[1]:.1f} %'
        if r[1] - r[2] > 0.05:
            lab += f'  (working {r[2]:.2f} %)' if r[2] < 1 else f'  (working {r[2]:.1f} %)'
        ax.text(r[1] + 0.8, i, lab, va='center', fontsize=8.5, color=INK2)
    ax.set_yticks(list(y)); ax.set_yticklabels([r[0] for r in rows])
    ax.set_xlim(0, 75); ax.set_xlabel('% of K12 proofs (155,000) that use the strategy')
    style(ax)
    ax.legend(loc='lower right', frameon=False, fontsize=8.5)
    ax.set_title('K12, the pretraining set: which strategies its proofs use', loc='left', fontsize=11.5, color=INK)
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, 'k12_mix.png'), dpi=160)
    plt.close(fig)


def fig_textbooks():
    sets = [('k12', 'K12 (generator proofs)', BLUE, 'o'), ('charles_base', "textbook problems (Charles's 187, reference proofs)", ORANGE, 'o'),
            ('tb_schema', 'textbook schemata in our RL pools (1,610, shortest proofs)', AQUA, 'D')]
    S = {s[0]: summ(s[0]) for s in sets}
    floor = 0.003

    def val(name, s):
        x = S[name]
        c = x['sub'][WORK[s]] if s in WORK else x['uses'][s]
        return max(100 * c / x['n'], floor), c == 0
    rows = [s for s in STRATS]
    ratio = lambda s: val('charles_base', s)[0] / val('k12', s)[0]
    rows.sort(key=ratio)
    fig, ax = plt.subplots(figsize=(8.6, 5.8))
    for i, s in enumerate(rows):
        xs = [val(nm, s)[0] for nm, *_ in sets]
        ax.plot([min(xs), max(xs)], [i, i], color=AXIS, linewidth=2, zorder=1)
        for k, (nm, lab, col, mk) in enumerate(sets):
            v, zero = val(nm, s)
            dy = (k - 1) * 0.22          # small vertical offsets so coinciding values stay visible
            ax.scatter([v], [i + dy], s=46 if mk == 'o' else 36, color=col, marker=mk, zorder=3, edgecolor=SURF, linewidth=1.5,
                       label=lab if i == 0 else None)
            if zero:
                ax.text(v * 1.6, i + dy, '0', va='center', fontsize=7.5, color=INK2)
        r = ratio(s)
        if r >= 3:
            ax.text(130, i, f'×{r:,.0f}', va='center', fontsize=8.5, color=INK2)
    ax.set_xscale('log'); ax.set_xlim(floor * 0.7, 300)
    ax.set_xticks([0.01, 0.1, 1, 10, 100]); ax.set_xticklabels(['0.01 %', '0.1 %', '1 %', '10 %', '100 %'])
    ax.set_yticks(range(len(rows)))
    ax.set_yticklabels([NAME[s] + (' — working' if s in WORK else '') for s in rows])
    ax.set_xlabel('% of proofs using the strategy (log scale); right: textbooks ÷ K12')
    style(ax)
    ax.legend(loc='lower left', frameon=False, fontsize=8.3, bbox_to_anchor=(0.0, 1.0), ncol=1)
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, 'k12_vs_textbooks.png'), dpi=160)
    plt.close(fig)


def fig_reductio():
    sets = [('k12', 'K12 (pretraining)'), ('k12dose1', 'dose set (K12⁻ + σ at 1 %)'),
            ('tb_schema_search', 'textbook laws (RL pools)'), ('charles_base', "textbook problems (Charles's 187)"), ('textbook72_search', 'textbook72')]
    rows = []
    for f, lab in sets:
        L = [json.loads(l) for l in gzip.open(f'artifacts/ps/labels/{f}.jsonl.gz', 'rt')]
        R = [a for a in L if not a.get('parse_fail') and 'contradiction' in a['u']]
        # each proof by its best instance: working > template (supplied or pointless) > vacuous
        wk = sum('contradiction.working' in a['sub'] for a in R)
        sup = sum('contradiction.working' not in a['sub'] and ('contradiction.scaffolded' in a['sub'] or 'contradiction.pointless' in a['sub']) for a in R)
        rows.append((lab, len(R), wk, sup, len(R) - wk - sup))
    rows = rows[::-1]
    fig, ax = plt.subplots(figsize=(9.2, 3.9))
    for i, (lab, n, wk, sup, vac) in enumerate(rows):
        left = 0
        for v, col in ((wk, BLUE), (sup, ORANGE), (vac, AQUA)):
            w = 100 * v / n if n else 0
            ax.barh(i, w, left=left, height=0.6, color=col, edgecolor=SURF, linewidth=2)
            if w >= 7:
                ax.text(left + w / 2, i, f'{w:.0f} %', ha='center', va='center', fontsize=8.5, color='white' if col != AQUA else INK)
            left += w
        ax.text(101.5, i, f'n = {n:,}' + (f' (working {wk:,})' if 0 < wk < 0.07 * n else ''), va='center', fontsize=8.5, color=INK2)
    ax.set_yticks(range(len(rows))); ax.set_yticklabels([r[0] for r in rows])
    ax.set_xlim(0, 140); ax.set_xticks([0, 25, 50, 75, 100]); ax.set_xticklabels(['0', '25', '50', '75', '100 %'])
    ax.set_xlabel('proofs that contain a proof by contradiction (n), each counted once by its best instance')
    style(ax)
    from matplotlib.patches import Patch
    ax.legend(handles=[Patch(color=BLUE, label='working: ¬G does more than clash at once with G or a supplied ¬¬G'),
                       Patch(color=ORANGE, label='template: ¬G clashes at once with a supplied ¬¬G, or G was already proved'),
                       Patch(color=AQUA, label='template, vacuous: ⊥ never uses ¬G (explosion in disguise)')],
              loc='lower left', bbox_to_anchor=(0.0, 1.0), frameon=False, fontsize=8.3)
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, 'reductio_kinds.png'), dpi=160)
    plt.close(fig)


if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    fig_mix(); fig_textbooks(); fig_reductio()
    print('figures written to', OUT)
