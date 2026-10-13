"""Figures for the create-or-elicit paper and blog, regenerated from the data files in this branch.

Run from the repository root:  python3 paper/scripts/figures.py [name ...]
Writes paper/figures/<name>.pdf and .png and prints, for every figure, the numbers it plots that the text quotes, so a
reader can check them against paper/LEDGER.md.

Models (every figure): best_model.ALiBiGPT 6 x 384, 9,560,832 parameters, lean_staten, trained from scratch; full = K12,
knockout = K12- (sigma+ removed, refilled), dose = K12^1% (1,550 sigma records put back); T1 expert iteration (k 32, T 0.8).
Lean 4 core alone judges every proof.

Data sources (all in git on this branch unless stated):
  review_coe/out_acq.json                  the create-or-elicit reviewer's recount of every read (strict sets)
  artifacts/coe/rounds/*.json              per-round ladder statistics (executor's coe_rounds.py; recounted in R5, R4)
  artifacts/coe/score/**/summary.json      teacher-forced log p of known sigma proofs (executor's; recounted in R11)
  artifacts/coe/budget/*.json              Phase 0.2 budgets and the compute-matched curve (recounted in R12)
  artifacts/coe/estimator/per_theorem.json Phase 0.1 estimator calibration (p-hat-bin table recounted in R12)
  paper/data/capdefs_j3.json               capability-defs J3 plain vs guided reads (fork dan_capability-defs da11be78)
  paper/data/mcts_a_summary.json           mcts-a solved counts (fork dan_mcts-a 5e70afbd)
"""
import json, math, os, statistics, sys

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.ticker import FuncFormatter, LogLocator

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
OUT = os.path.join(ROOT, 'paper', 'figures')
os.makedirs(OUT, exist_ok=True)

# Palette: validated (dataviz validate_palette.js, light, all pairs: CVD dE >= 9.2, normal >= 24.0). Aqua is below 3:1
# contrast on the surface, so every arm is also direct-labelled and has its own marker shape.
FULL, KO, DOSE = '#2a78d6', '#eb6834', '#1baf7a'
ARM_COLOR = {'full': FULL, 'ko': KO, 'dose1': DOSE}
ARM_MARK = {'full': 'o', 'ko': 's', 'dose1': '^'}
ARM_NAME = {'full': 'full exposure', 'ko': 'knockout (no σ)', 'dose1': '1 % σ dose'}
SEEDS = {'full': range(6), 'ko': range(6), 'dose1': range(3)}
INK, INK2, INK3 = '#0b0b0b', '#52514e', '#8a8984'
GRID, SURF = '#e4e3df', '#ffffff'
BLUES = ['#cde2fb', '#9ec5f4', '#6da7ec', '#3987e5', '#2a78d6', '#1c5cab', '#104281', '#0d366b']
FAMS = ['contraposition_conv', 'negated_conditional', 'peirce', 'peirce_sequent', 'excluded_middle', 'demorgan_nand_to_or']
FAM_SHORT = {'contraposition_conv': 'contrap.\nconv.', 'negated_conditional': 'neg.\ncond.',
             'peirce': 'Peirce', 'peirce_sequent': 'Peirce\nseq.', 'excluded_middle': 'excl.\nmiddle',
             'demorgan_nand_to_or': 'De\nMorgan'}

plt.rcParams.update({
    'font.size': 8.5, 'axes.titlesize': 9, 'axes.labelsize': 8.5, 'xtick.labelsize': 8, 'ytick.labelsize': 8,
    'legend.fontsize': 7.5, 'axes.edgecolor': INK3, 'axes.labelcolor': INK, 'xtick.color': INK2, 'ytick.color': INK2,
    'axes.grid': True, 'grid.color': GRID, 'grid.linewidth': 0.6, 'axes.facecolor': SURF, 'figure.facecolor': SURF,
    'axes.spines.top': False, 'axes.spines.right': False, 'axes.titlelocation': 'left', 'axes.titleweight': 'bold',
    'lines.solid_capstyle': 'round', 'lines.solid_joinstyle': 'round', 'savefig.dpi': 200, 'pdf.fonttype': 42,
})


def J(path):
    with open(os.path.join(ROOT, path)) as f:
        return json.load(f)


def save(fig, name):
    for ext in ('pdf', 'png'):
        fig.savefig(os.path.join(OUT, f'{name}.{ext}'), bbox_inches='tight', facecolor=SURF)
    plt.close(fig)
    print(f'wrote paper/figures/{name}.pdf / .png')


def acq():
    return J('review_coe/out_acq.json')['reads']


# ---------------------------------------------------------------- F1: the endpoint
def fig_endpoint():
    R = acq()
    fig, (a, b) = plt.subplots(1, 2, figsize=(7.2, 3.3), gridspec_kw={'width_ratios': [1.0, 1.15]})
    xs = {'pend': 0, 'r8': 8, 'r16': 16, 'r20': 20, 'r24': 24}
    printed = {}
    for arm in ('full', 'dose1', 'ko'):
        for s in SEEDS[arm]:
            pts = [(xs[ck], R[f'{ck}_{arm}_s{s}_x0']['strict']['solved']) for ck in ('pend', 'r8', 'r16')
                   if f'{ck}_{arm}_s{s}_x0' in R]
            printed[f'{arm}_s{s}'] = [y for _, y in pts]
            jitter = (s - 2.5) * 0.12
            a.plot([x + jitter for x, _ in pts], [y for _, y in pts], color=ARM_COLOR[arm], lw=1.4, alpha=0.9,
                   marker=ARM_MARK[arm], ms=4.5, mec=SURF, mew=0.8, zorder=3)
            if arm == 'ko' and s == 1:
                ext = [(xs[ck], R[f'{ck}_ko_s1_x0']['strict']['solved']) for ck in ('r16', 'r20', 'r24')]
                printed['ko_s1_ext'] = [y for _, y in ext]
                a.plot([x + jitter for x, _ in ext], [y for _, y in ext], color=KO, lw=1.2, ls=(0, (2, 2)),
                       marker='s', ms=4.5, mec=SURF, mew=0.8, zorder=3)
    a.set_xticks([0, 8, 16, 20, 24]); a.set_xticklabels(['pend', 'r8', 'r16', 'r20', 'r24'])
    a.set_xlim(-1.5, 34); a.set_ylim(-3, 106)
    a.set_ylabel('strict held-out family members solved (of 106)')
    a.set_xlabel('checkpoint (EI round); plain read, k 256')
    a.text(25.5, 62, 'full exposure\n6 seeds', color=FULL, fontsize=8, va='center', fontweight='bold')
    a.text(25.5, 40, '1 % σ dose\n3 seeds', color=DOSE, fontsize=8, va='center', fontweight='bold')
    a.text(25.5, 12, 'knockout\n6 seeds', color=KO, fontsize=8, va='center', fontweight='bold')
    a.text(19.5, 21, 's1 continued\n(exploratory)', color=INK2, fontsize=6.8, va='center')
    a.annotate('', xy=(22, 6.5), xytext=(21.5, 16.5), arrowprops=dict(arrowstyle='-', color=INK3, lw=0.7))
    a.set_title('a  Acquisition of the classical families')

    # b: per family at r16, rows = ladders, cell = fraction of the family's strict members solved; dot = at the bar
    rows = [('full', s) for s in range(6)] + [('dose1', s) for s in range(3)] + [('ko', s) for s in range(6)]
    import numpy as np
    from matplotlib.colors import LinearSegmentedColormap
    cmap = LinearSegmentedColormap.from_list('b', ['#f4f8fe'] + BLUES[1:7])
    M = np.zeros((len(rows), len(FAMS)))
    bar = np.zeros_like(M, dtype=bool)
    for i, (arm, s) in enumerate(rows):
        pf = R[f'r16_{arm}_s{s}_x0']['strict']['per_family']
        for j, f in enumerate(FAMS):
            k, n = pf[f]
            M[i, j] = k / n
            bar[i, j] = k / n >= 0.5
    b.imshow(M, cmap=cmap, vmin=0, vmax=1, aspect='auto')
    for i in range(len(rows)):
        for j in range(len(FAMS)):
            if bar[i, j]:
                b.plot(j, i, 'o', ms=4.2, color=SURF, mec=INK, mew=0.9)
    b.set_xticks(range(len(FAMS)))
    n_strict = R['r16_full_s0_x0']['strict']['per_family']
    b.set_xticklabels([f'{FAM_SHORT[f]}\n(n={n_strict[f][1]})' for f in FAMS], fontsize=6.6)
    b.set_yticks(range(len(rows)))
    b.set_yticklabels([f"{ {'full': 'full', 'dose1': 'dose', 'ko': 'knockout'}[arm]} s{s}" for arm, s in rows], fontsize=7)
    for t, (arm, _) in zip(b.get_yticklabels(), rows):
        t.set_color(ARM_COLOR[arm])
    b.grid(False)
    for y in (5.5, 8.5):
        b.axhline(y, color=SURF, lw=2.5)
    b.tick_params(length=0)
    for sp in b.spines.values():
        sp.set_visible(False)
    b.set_title('b  Per family at r16 (● = at the bar, ≥ 50 %)')
    cb = fig.colorbar(b.images[0], ax=b, fraction=0.04, pad=0.02)
    cb.ax.tick_params(labelsize=7); cb.outline.set_visible(False)
    fig.tight_layout()
    save(fig, 'fig1_endpoint')
    print('  strict solved pend/r8/r16 x0:', printed)


# ---------------------------------------------------------------- F2: ladder dynamics
def _ladders():
    out = []
    for s in range(3):
        out.append(('full', s, f'artifacts/coe/rounds/old_full_s{s}.json'))
    for s in range(3, 6):
        out.append(('full', s, f'artifacts/coe/rounds/la_full_s{s}.json'))
    for s in range(3):
        out.append(('dose1', s, f'artifacts/coe/rounds/la_dose1_s{s}.json'))
    for s in range(6):
        out.append(('ko', s, f'artifacts/coe/rounds/la_ko_s{s}.json'))
    return out


def free_plus_per_round(d):
    """Accepted proofs in a round's k 32 sample whose DN step is a free positive reductio (any route; coe_rounds.sigma_subtype)."""
    return {int(r): sum(v for k, v in sub.items() if k.startswith('pos_free')) for r, sub in d['sigma_subtypes_by_round'].items()}


def fig_dynamics():
    fig, (a, b) = plt.subplots(1, 2, figsize=(7.2, 3.0))
    printed = {}
    for arm, s, path in _ladders():
        d = J(path)
        rr = sorted(int(r) for r in d['per_round'])
        cum = [d['per_round'][str(r)]['sigma_targets_cum'] for r in rr]
        fp = free_plus_per_round(d)
        fpl = [fp.get(r, 0) for r in rr]
        printed[f'{arm}_s{s}'] = {'targets_cum_r1_r16': (cum[0], cum[min(15, len(cum) - 1)]),
                                  'free+_r16': fpl[min(15, len(fpl) - 1)], 'free+_first_round': next((r for r, v in zip(rr, fpl) if v > 0), None)}
        for ax, ys in ((a, cum), (b, fpl)):
            k16 = [i for i, r in enumerate(rr) if r <= 16]
            ax.plot([rr[i] for i in k16], [ys[i] for i in k16], color=ARM_COLOR[arm], lw=1.3, alpha=0.9)
            if len(rr) > 16:
                ext = [i for i, r in enumerate(rr) if r >= 16]
                ax.plot([rr[i] for i in ext], [ys[i] for i in ext], color=ARM_COLOR[arm], lw=1.2, ls=(0, (2, 2)))
        if arm == 'ko' and s == 1:
            printed['ko_s1_free+_r9_r24'] = fpl[8:24]
    a.set_xlabel('EI round'); a.set_ylabel('strict trained targets solved (of 123)')
    a.set_title('a  Targets that need the reductio')
    a.set_xlim(0.5, 24.5); a.set_ylim(-3, 92)
    b.set_yscale('symlog', linthresh=1, linscale=0.6)
    b.set_ylim(-0.3, 1.2e5)
    b.set_xlabel('EI round'); b.set_ylabel('accepted proofs in the round (k 32 sample)')
    b.set_title('b  Free reductio proofs per round')
    b.set_xlim(0.5, 24.5)
    handles = [Line2D([], [], color=ARM_COLOR[k], lw=1.6, label=ARM_NAME[k]) for k in ('full', 'dose1', 'ko')]
    handles.append(Line2D([], [], color=KO, lw=1.2, ls=(0, (2, 2)), label='knockout s1, r17–r24 (exploratory)'))
    a.legend(handles=handles, loc='upper left', frameon=False)
    fig.tight_layout()
    save(fig, 'fig2_dynamics')
    for k, v in printed.items():
        print('  ', k, v)


# ---------------------------------------------------------------- F3: log p of known sigma proofs along the ladders
def fig_logp():
    fig, ax = plt.subplots(figsize=(4.4, 3.1))
    base = J('artifacts/coe/score/summary.json')['ckpts']
    pts = {}
    order = ['pend', 'r4', 'r8', 'r12', 'r16']
    xs = {'pend': 0, 'r4': 4, 'r8': 8, 'r12': 12, 'r16': 16}
    for arm, seeds in (('full', (3, 4, 5)), ('dose1', (0, 1, 2)), ('ko', range(6))):
        for s in seeds:
            p = f'artifacts/coe/score/rounds_{arm}_s{s}/summary.json'
            if not os.path.exists(os.path.join(ROOT, p)):
                continue
            c = J(p)['ckpts']
            ys = [(xs[k], c[k]['heldout']['best_median']) for k in order if k in c]
            pts[f'{arm}_s{s}'] = [round(y, 1) for _, y in ys]
            ax.plot([x for x, _ in ys], [y for _, y in ys], color=ARM_COLOR[arm], lw=1.4, marker=ARM_MARK[arm], ms=4,
                    mec=SURF, mew=0.7)
    ax.plot([0], [base['full_s0']['heldout']['best_median']], marker='o', ms=5, color=FULL, mec=INK, mew=0.6, ls='none')
    pts['full_s0_pend'] = round(base['full_s0']['heldout']['best_median'], 1)
    ax.set_xticks([0, 4, 8, 12, 16]); ax.set_xticklabels(['pend', 'r4', 'r8', 'r12', 'r16'])
    ax.set_ylabel('median log p of best known σ proof (nats)')
    ax.set_xlabel('checkpoint')
    ax.set_title('Distance to the reductio along each ladder')
    ax.text(16.6, -6, 'full', color=FULL, fontsize=8, fontweight='bold', va='center')
    ax.text(16.6, -16, 'dose', color=DOSE, fontsize=8, fontweight='bold', va='center')
    ax.text(16.6, -33, 'knockout', color=KO, fontsize=8, fontweight='bold', va='center')
    ax.set_xlim(-1, 21)
    fig.tight_layout()
    save(fig, 'fig3_logp')
    print('  ', pts)


# ---------------------------------------------------------------- F4: the compute-matched set is a curve in K
def fig_budget():
    g = J('artifacts/coe/budget/part3_recount_grid.json')
    bj = J('artifacts/coe/budget/budget.json')
    fig, ax = plt.subplots(figsize=(5.6, 3.3))
    defs = [('K_att', 'target attempts (K_att)', 'v'), ('K_train_sameclass', 'training phases (K_train)', 's'),
            ('K_evalset_sameclass', 'all ladder GPU time (K_uni)', 'D'), ('K_pub', 'as published (K_pub)', 'o'),
            ('K_adapt', 'adaptive (K_adapt)', '^')]
    shades = ['#86b6ef', '#2a78d6', '#104281']
    printed = {}
    for i, s in enumerate(('0', '1', '2')):
        rows = sorted((v['K'], v['cm'], v['cm_undet']) for k, v in g['sens'][f's{s}'].items() if k.startswith('K x'))
        rows = [r for r in rows if r[2] == 0]
        ax.step([r[0] for r in rows], [r[1] for r in rows], where='post', color=shades[i], lw=1.8)
        ax.text(rows[-1][0] * 1.35, rows[-1][1] + (0.9 if s == '0' else -0.6 if s == '1' else 0), f'seed {s}', color=INK2, fontsize=7.5, va='center')
        r8 = bj['per_seed'][s]['r8']
        printed[s] = {}
        for kk, lab, m in defs:
            K = r8[kk]
            cm = min(rows, key=lambda r: abs(math.log(r[0] / K)))[1]
            printed[s][kk] = (round(K), cm)
            ax.plot([K], [cm], marker=m, ms=6.5, color=shades[i], mec=INK, mew=0.7, ls='none', zorder=4)
    ax.set_xscale('log')
    ax.xaxis.set_major_locator(LogLocator(base=10))
    ax.xaxis.set_major_formatter(FuncFormatter(lambda v, _: f'{int(v):,}'))
    ax.set_xlim(1000, 3e5); ax.set_ylim(0, 45)
    ax.set_xlabel('budget K: base attempts per evaluation theorem')
    ax.set_ylabel('theorems RL r8 solves that the\nbase cannot reach within K')
    ax.set_title('"Created" depends on the budget')
    handles = [Line2D([], [], marker=m, color=INK2, mfc=SURF, mec=INK, ls='none', ms=6, label=lab) for _, lab, m in defs]
    ax.legend(handles=handles, loc='upper right', frameon=False, title='budget allocation', title_fontsize=7.5)
    fig.tight_layout()
    save(fig, 'fig4_budget')
    print('  (K, set) per seed and allocation:', printed)


# ---------------------------------------------------------------- F5: the known-proof estimator
def fig_estimator():
    E = J('artifacts/coe/estimator/per_theorem.json')
    fig, (a, b) = plt.subplots(1, 2, figsize=(7.0, 3.0), gridspec_kw={'width_ratios': [1.1, 1]})
    shades = ['#86b6ef', '#2a78d6', '#104281']
    bins = [('≥1e-3', lambda p: p >= 1e-3), ('1e-4–1e-3', lambda p: 1e-4 <= p < 1e-3),
            ('1e-5–1e-4', lambda p: 1e-5 <= p < 1e-4), ('<1e-5', lambda p: 0 < p < 1e-5)]
    ratios = {k: [] for k, _ in bins}
    for i, s in enumerate(('0', '1', '2')):
        xs, ys = [], []
        for t, r in E[s].items():
            if r.get('c', 0) >= 1 and r.get('E_all') and r.get('phat'):
                xs.append(r['phat']); ys.append(r['E_all'])
                for k, f in bins:
                    if f(r['phat']):
                        ratios[k].append(r['E_all'] / r['phat'])
        a.scatter(xs, ys, s=10, color=shades[i], edgecolor=SURF, linewidth=0.4, label=f'seed {s}', zorder=3)
    lo, hi = 3e-7, 1.5
    a.plot([lo, hi], [lo, hi], color=INK2, lw=1)
    a.plot([lo, hi], [lo / 2, hi / 2], color=INK3, lw=0.8, ls=(0, (3, 2)))
    a.text(2e-6, 3.2e-6, 'estimate = p̂', color=INK2, fontsize=7, rotation=33)
    a.text(4e-6, 1.1e-6, 'p̂ / 2', color=INK3, fontsize=7, rotation=33)
    a.set_xscale('log'); a.set_yscale('log'); a.set_xlim(lo, hi); a.set_ylim(1e-9, hi)
    a.set_xlabel('measured p̂ (successes / attempts)'); a.set_ylabel('known-proof estimate E')
    a.set_title('a  Estimate vs sampling (pend s0–s2)')
    a.legend(loc='upper left', frameon=False)
    names = [k for k, _ in bins]
    med = [statistics.median(ratios[k]) if ratios[k] else float('nan') for k in names]
    p10 = [sorted(ratios[k])[int(0.1 * (len(ratios[k]) - 1))] if ratios[k] else float('nan') for k in names]
    p90 = [sorted(ratios[k])[int(0.9 * (len(ratios[k]) - 1))] if ratios[k] else float('nan') for k in names]
    for j, k in enumerate(names):
        b.plot([j, j], [p10[j], p90[j]], color=FULL, lw=2, alpha=0.5)
        b.plot([j], [med[j]], 'o', color=FULL, ms=6, mec=SURF, mew=1)
        b.text(j + 0.12, med[j], f'{med[j]:.2f}\n(n={len(ratios[k])})', fontsize=7, color=INK2, va='center')
    b.axhline(1, color=INK2, lw=1)
    b.set_xticks(range(len(names))); b.set_xticklabels(names)
    b.set_yscale('log'); b.set_ylim(0.03, 5)
    b.set_xlabel('measured p̂ bin'); b.set_ylabel('estimate / p̂ (median, 10–90 %)')
    b.set_title('b  The estimate runs low below 10⁻⁴')
    fig.tight_layout()
    save(fig, 'fig5_estimator')
    print('  median ratio by p-hat bin:', dict(zip(names, [round(m, 3) for m in med])), {k: len(v) for k, v in ratios.items()})


# ---------------------------------------------------------------- F6: base prior vs acquisition (exploratory, post hoc)
def fig_prior():
    R = acq()
    base = J('artifacts/coe/score/summary.json')['ckpts']
    pts = []
    for arm, seeds in (('full', (0, 3, 4, 5)), ('dose1', (0, 1, 2)), ('ko', range(6))):
        for s in seeds:
            if arm == 'full' and s == 0:
                lp = base['full_s0']['heldout']['best_median']
            elif arm == 'ko':
                lp = base[f'ko_s{s}']['heldout']['best_median']
            else:
                lp = J(f'artifacts/coe/score/rounds_{arm}_s{s}/summary.json')['ckpts']['pend']['heldout']['best_median']
            pts.append((arm, s, lp, R[f'r16_{arm}_s{s}_x0']['strict']['solved']))
    from scipy.stats import spearmanr
    rho, p = spearmanr([x[2] for x in pts], [x[3] for x in pts])
    rho_nonko, p_nonko = spearmanr([x[2] for x in pts if x[0] != 'ko'], [x[3] for x in pts if x[0] != 'ko'])
    fig, ax = plt.subplots(figsize=(4.4, 3.1))
    for arm, s, lp, y in pts:
        ax.plot(lp, y, marker=ARM_MARK[arm], color=ARM_COLOR[arm], ms=7, mec=SURF, mew=1, ls='none')
        ax.text(lp + 0.4, y + 1.5, f's{s}', fontsize=6.5, color=INK2)
    ax.set_xlabel('base (pend): median log p of best known σ proof (nats)')
    ax.set_ylabel('strict held-out members solved at r16 (of 106)')
    ax.set_title('Base prior and later acquisition (exploratory)')
    handles = [Line2D([], [], marker=ARM_MARK[k], color=ARM_COLOR[k], ls='none', ms=6, label=ARM_NAME[k]) for k in ('full', 'dose1', 'ko')]
    ax.legend(handles=handles, loc='upper left', frameon=False)
    fig.tight_layout()
    save(fig, 'fig6_prior')
    print(f'  Spearman rho over {len(pts)} ladders = {rho:.3f} (p {p:.2g}); without knockout ({sum(1 for x in pts if x[0] != "ko")}) rho = {rho_nonko:.3f} (p {p_nonko:.2g})')
    print('  points:', [(a, s, round(lp, 1), y) for a, s, lp, y in pts])
    return {'rho': rho, 'p': p, 'rho_nonko': rho_nonko, 'p_nonko': p_nonko, 'points': pts}


# ---------------------------------------------------------------- F7: test-time compute before and after RL
def fig_ttc():
    j3 = J('paper/data/capdefs_j3.json')
    mc = J('paper/data/mcts_a_summary.json')['tables']
    fig, (a, b) = plt.subplots(1, 2, figsize=(7.2, 3.0))
    ck_col = {'pend': '#86b6ef', 'r8': '#2a78d6', 'r16': '#104281'}
    printed = {'guided': {}, 'mcts': {}}
    for gi, pool in enumerate(('tb72', 'h250')):
        for ci, ck in enumerate(('pend', 'r8', 'r16')):
            gains = [j3[f'c12_s{s}_{ck}'][pool]['guided'] - j3[f'c12_s{s}_{ck}'][pool]['plain'] for s in range(3)]
            printed['guided'][f'{pool}_{ck}'] = gains
            x0 = gi * 4 + ci
            a.bar(x0, statistics.mean(gains), width=0.7, color=ck_col[ck], zorder=2)
            a.plot([x0 - 0.12, x0, x0 + 0.12], gains, 'o', color=INK, ms=3, zorder=3)
    a.set_xticks([1, 5]); a.set_xticklabels(['textbook72 (72)', 'holdout250 (250)'])
    a.axhline(0, color=INK2, lw=0.8)
    a.set_ylabel('guided − plain, theorems solved at k 256')
    a.set_title('a  Guided step redraws')
    handles = [plt.Rectangle((0, 0), 1, 1, color=ck_col[k], label=k) for k in ('pend', 'r8', 'r16')]
    a.legend(handles=handles, loc='upper right', frameon=False, title='checkpoint', title_fontsize=7.5)
    pools = [('C', 'group C\n(28–36)'), ('tb72', 'textbook\n72'), ('h250', 'holdout\n250'), ('rrQ100', 'long\nrrQ100'), ('long2', 'long2\n(21)')]
    for pi, (p, lab) in enumerate(pools):
        for ci, ck in enumerate(('pend', 'r8')):
            t = mc[f'{ck}/{p}']
            d = [t[f'value/s{s}'] - t[f'sample/s{s}'] for s in range(3)]
            printed['mcts'][f'{ck}/{p}'] = d
            x0 = pi * 3 + ci
            b.bar(x0, statistics.mean(d), width=0.8, color=ck_col[ck], zorder=2)
            b.plot([x0 - 0.15, x0, x0 + 0.15], d, 'o', color=INK, ms=3, zorder=3)
    b.set_xticks([pi * 3 + 0.5 for pi in range(len(pools))]); b.set_xticklabels([l for _, l in pools], fontsize=7)
    b.axhline(0, color=INK2, lw=0.8)
    b.set_ylabel('PUCT + value − sampling, theorems solved')
    b.set_title('b  Tree search at matched wall clock')
    b.legend(handles=handles[:2], loc='upper left', frameon=False, title='checkpoint', title_fontsize=7.5)
    fig.tight_layout()
    save(fig, 'fig7_ttc')
    print('  ', printed)


FIGS = {'endpoint': fig_endpoint, 'dynamics': fig_dynamics, 'logp': fig_logp, 'budget': fig_budget,
        'estimator': fig_estimator, 'prior': fig_prior, 'ttc': fig_ttc}

if __name__ == '__main__':
    names = sys.argv[1:] or list(FIGS)
    for n in names:
        print(f'== {n}')
        FIGS[n]()
