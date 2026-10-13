#!/usr/bin/env python3
"""create-or-elicit: paper figures (vector PDF + 200-dpi PNG in figures/).  Palette: the dataviz reference instance
(validated: categorical slots 1-3 pass CVD / normal-vision checks on the light surface; aqua and the yellow slot sit below
3:1 contrast, so every series is also direct-labelled or in the legend, and every figure has a table in the write-up).

  python3 coe/coe_figures.py estimator      # figures/coe_estimator.{pdf,png}   (Phase 0.1)
  python3 coe/coe_figures.py budget         # figures/coe_budget.{pdf,png}      (Phase 0.2)
"""
import json, math, os, sys
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

SER = ['#2a78d6', '#eb6834', '#1baf7a', '#eda100', '#e87ba4', '#008300', '#4a3aa7', '#e34948']
INK, INK2, MUTED, GRID, AXIS, SURF = '#0b0b0b', '#52514e', '#898781', '#e1e0d9', '#c3c2b7', '#ffffff'
plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 9, 'axes.edgecolor': AXIS, 'axes.labelcolor': INK2,
                     'xtick.color': MUTED, 'ytick.color': MUTED, 'axes.titlecolor': INK, 'axes.titlesize': 10,
                     'axes.grid': True, 'grid.color': GRID, 'grid.linewidth': 0.6, 'axes.facecolor': SURF,
                     'figure.facecolor': SURF, 'legend.frameon': False, 'lines.linewidth': 2.0,
                     'axes.spines.top': False, 'axes.spines.right': False})
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')


def save(fig, name):
    for ext in ('pdf', 'png'):
        fig.savefig(os.path.join(ROOT, 'figures', f'{name}.{ext}'), dpi=200, bbox_inches='tight')
    print('wrote figures/%s.{pdf,png}' % name)


def estimator():
    per = json.load(open(os.path.join(ROOT, 'artifacts/coe/estimator/per_theorem.json')))
    summ = json.load(open(os.path.join(ROOT, 'artifacts/coe/estimator/summary.json')))
    fig, (a, b) = plt.subplots(1, 2, figsize=(9.2, 3.9), gridspec_kw={'width_ratios': [1.25, 1]})
    for i, s in enumerate(sorted(per)):
        xs, ys, lo, hi = [], [], [], []
        for t, r in per[s].items():
            if r['c'] >= 1 and r.get('E_all'):
                xs.append(r['phat']); ys.append(r['E_all']); lo.append(r['phat'] - r['cp_lo']); hi.append(r['cp_hi'] - r['phat'])
        a.errorbar(xs, ys, xerr=[lo, hi], fmt='o', ms=4, color=SER[i], ecolor=SER[i], elinewidth=0.6, alpha=0.85,
                   mec=SURF, mew=0.6, label=f'pend s{s} ({len(xs)} theorems)')
    lim = (3e-7, 0.5)
    a.plot(lim, lim, color=INK2, lw=1.0, label='y = x (dashed: ×2 and ÷2)')
    a.plot(lim, [2 * v for v in lim], color=MUTED, lw=0.8, ls='--')
    a.plot(lim, [v / 2 for v in lim], color=MUTED, lw=0.8, ls='--')
    a.axvline(1e-4, color=MUTED, lw=0.8, ls=':')
    a.text(1.15e-4, 2e-1, 'p̂ = 10⁻⁴', color=INK2, fontsize=8)
    a.set_xscale('log'); a.set_yscale('log'); a.set_xlim(*lim); a.set_ylim(1e-8, 1)
    a.set_xlabel('measured p̂ = successes / attempts (95 % CP interval)'); a.set_ylabel('known-proof estimate E = Σ π(proof)')
    a.set_title('(a) estimate vs sampled rate, theorems with ≥ 1 success', loc='left')
    a.legend(loc='lower right', fontsize=8)
    order = ['ge1e-3', '1e-4..1e-3', '1e-5..1e-4', '1e-6..1e-5', 'lt1e-6']
    labels = ['≥ 10⁻³', '10⁻⁴–10⁻³', '10⁻⁵–10⁻⁴', '10⁻⁶–10⁻⁵', '< 10⁻⁶']
    eb = summ['ebins']['all']
    xs = list(range(len(order)))
    v = [eb[k]['obs_over_pred'] for k in order]
    ci = [eb[k]['obs_over_pred_ci95'] for k in order]
    b.errorbar(xs, v, yerr=[[vv - c[0] for vv, c in zip(v, ci)], [c[1] - vv for vv, c in zip(v, ci)]], fmt='o', ms=7,
               color=SER[0], ecolor=SER[0], elinewidth=1.2, capsize=0, mec=SURF, mew=1.0)
    for x, vv, k in zip(xs, v, order):
        b.text(x + 0.12, vv + 0.45, f'{vv:.2f} (n {eb[k]["n"]})', color=INK2, fontsize=7.5, va='bottom')
    b.axhline(1.0, color=INK2, lw=1.0)
    b.set_xticks(xs); b.set_xticklabels(labels, rotation=20)
    b.set_xlabel('bin of the estimate E (selection-free)'); b.set_ylabel('observed / predicted base successes')
    b.set_ylim(0, 9.5); b.set_xlim(-0.4, len(order) - 0.2)
    b.set_title('(b) calibration by estimate bin, all 330 theorems', loc='left')
    fig.suptitle('Known-proof estimator, best-cap12 pend s0–s2 (9.56 M, lean_staten, from scratch on K12), T 0.8, Lean alone',
                 x=0.01, ha='left', fontsize=9, color=INK2)
    fig.tight_layout()
    save(fig, 'coe_estimator')


def budget():
    g = json.load(open(os.path.join(ROOT, 'artifacts/coe/budget/part3_recount_grid.json')))
    b = json.load(open(os.path.join(ROOT, 'artifacts/coe/budget/budget.json')))
    fig, ax = plt.subplots(figsize=(7.6, 4.2))
    defs = [('K_att', 'mul_att', 'ladder target attempts'), ('K_train_sameclass', 'mul_train', 'K_train (training phases)'),
            ('K_evalset_sameclass', 'mul_evalset', 'K_eval-set, same class'), ('K_pub', None, 'K_eval-set as published'),
            ('K_adapt', 'mul_adapt', 'adaptive allocation')]
    marks = ['v', 's', 'D', 'o', '^']
    for i, s in enumerate(('0', '1', '2')):
        rows = sorted((v['K'], v['cm'], v['cm_undet']) for k, v in g['sens'][f's{s}'].items() if k.startswith('K x'))
        rows = [r for r in rows if r[2] == 0]
        ax.step([r[0] for r in rows], [r[1] for r in rows], where='post', color=SER[i], lw=2.0)
        ax.text(rows[-1][0] * 1.04, rows[-1][1], f's{s}', color=INK2, fontsize=9, va='center')
        r8 = b['per_seed'][s]['r8']
        for (kk, mk, lab), m in zip(defs, marks):
            K = r8[kk]
            cm = min(rows, key=lambda r: abs(math.log(r[0] / K)))[1]     # the grid contains every definition's exact K
            ax.plot([K], [cm], marker=m, ms=8, color=SER[i], mec=INK, mew=0.8, ls='none',
                    label=lab if i == 0 else None)
    for m, lab in zip(marks, [d[2] for d in defs]):
        pass
    ax.set_xscale('log')
    ax.set_xlabel('budget K: base attempts per evaluation theorem (r8 ladder compute)')
    ax.set_ylabel('compute-matched set: RL r8 solves, base not within reach')
    ax.set_title('The "created at matched compute" set depends on how the budget is allocated', loc='left')
    leg = ax.legend(loc='lower left', fontsize=8, title='budget definition (marker)', title_fontsize=8)
    for h in getattr(leg, 'legend_handles', None) or leg.legendHandles:
        h.set_color(INK2); h.set_markerfacecolor(SURF)
    fig.text(0.01, -0.02, 'Lines: full seeds s0 / s1 / s2 (best-cap12 r8 vs its pend: 9.56 M, lean_staten, from scratch on K12; Lean alone). '
             'Budget-robust core (0 base successes in ≥ 66,304 attempts): 18 / 17 / 8.', fontsize=7.5, color=INK2)
    ax.set_ylim(0, 42)
    from matplotlib.ticker import LogLocator, FuncFormatter
    ax.xaxis.set_major_locator(LogLocator(base=10, subs=(1.0, 2.0, 5.0)))
    ax.xaxis.set_major_formatter(FuncFormatter(lambda v, _: f'{int(v):,}'))
    fig.tight_layout()
    save(fig, 'coe_budget')


def _rounds_series():
    import glob
    out = []
    for fn in sorted(glob.glob(os.path.join(ROOT, 'artifacts/coe/rounds/*.json'))):
        b = os.path.basename(fn)
        if b.startswith('la_full_s'):
            arm, seed = 'full', int(b[len('la_full_s'):-5])
        elif b.startswith('old_full_s'):
            arm, seed = 'full', int(b[len('old_full_s'):-5])
        elif b.startswith('la_ko_s'):
            arm, seed = 'knockout', int(b[len('la_ko_s'):-5])
        else:
            continue
        d = json.load(open(fn))
        rs = sorted(int(r) for r in d['per_round'])
        tgt = [d['per_round'][str(r)]['sigma_targets_cum'] for r in rs]
        st = d.get('sigma_subtypes_by_round', {})
        free = [(st.get(str(r), {}).get('pos_free', 0) + st.get(str(r), {}).get('pos_free_impi', 0)) for r in rs]
        out.append((arm, seed, rs, tgt, free))
    return out


def rounds():
    ser = _rounds_series()
    col = {'full': SER[0], 'knockout': SER[1]}
    fig, (a, b) = plt.subplots(1, 2, figsize=(9.6, 3.8))
    seen = set()
    for arm, seed, rs, tgt, free in ser:
        lab = None if arm in seen else f"{arm} ({sum(1 for x in ser if x[0] == arm)} seeds)"
        seen.add(arm)
        a.plot(rs, tgt, color=col[arm], lw=1.6, alpha=0.9, label=lab, marker='o', ms=3)
        b.plot(rs, [f + 0.5 for f in free], color=col[arm], lw=1.6, alpha=0.9, label=lab, marker='o', ms=3)
    a.set_xlabel('EI round'); a.set_ylabel('strict σ-covered training targets solved (of 123)')
    a.set_title('(a) classical targets that need σ', loc='left'); a.set_ylim(-3, 125); a.set_xlim(0.5, 16.5)
    a.legend(loc=(0.52, 0.06), fontsize=8)
    b.set_yscale('log'); b.set_xlabel('EI round'); b.set_ylabel('accepted proofs with free positive σ (+0.5)')
    b.set_title('(b) proofs that build ¬¬G for a goal G the theorem never negates', loc='left', fontsize=9); b.set_xlim(0.5, 16.5)
    fig.text(0.01, -0.03, 'Full: K12 bases s0–s5 (s0–s2 trajectory + rl-continue, s3–s5 this run); knockout: K12⁻ bases s0–s5 (this run). '
             '9.56 M ALiBiGPT, lean_staten, T1 EI k 32; Lean alone.', fontsize=7.5, color=INK2)
    fig.tight_layout()
    save(fig, 'coe_rounds')


def endpoint():
    d = json.load(open(os.path.join(ROOT, 'artifacts/coe/compare_r16_x0.json')))
    seeds = d['seeds']
    fams = ['contraposition_conv', 'negated_conditional', 'peirce', 'peirce_sequent', 'excluded_middle', 'demorgan_nand_to_or']
    share = {'ko': 0.0, 'dose1': 1.0, 'full': 10.8}
    lab = {'ko': 'knockout (0 %)', 'dose1': '1 % dose', 'full': 'full (10.8 %)'}
    col = {'ko': SER[1], 'dose1': SER[2], 'full': SER[0]}
    arms = [a for a in ('ko', 'dose1', 'full') if any(v['arm'] == a for v in seeds.values())]
    fig, (a, b) = plt.subplots(1, 2, figsize=(10.0, 3.9), gridspec_kw={'width_ratios': [1, 1.25]})
    for i, arm in enumerate(arms):
        ys = sorted(v['strict_heldout_solved'] for v in seeds.values() if v['arm'] == arm)
        xs = [i + (j - (len(ys) - 1) / 2) * 0.07 for j in range(len(ys))]
        a.plot(xs, ys, 'o', ms=7, color=col[arm], mec=SURF, mew=1.0)
        med = sorted(ys)[len(ys) // 2] if len(ys) % 2 else (ys[len(ys) // 2 - 1] + ys[len(ys) // 2]) / 2
        a.plot([i - 0.25, i + 0.25], [med, med], color=INK2, lw=1.2)
        a.text(i + 0.28, med, f'median {med:g}', color=INK2, fontsize=8, va='center')
    a.set_xticks(range(len(arms))); a.set_xticklabels([lab[x] for x in arms])
    a.set_xlabel('share of σ records in pretraining'); a.set_ylabel('held-out members solved at r16 (of 106)')
    a.set_xlim(-0.5, len(arms) - 0.3); a.set_ylim(-4, 110)
    a.set_title('(a) after 16 EI rounds, per seed', loc='left')
    rows = [k for k in sorted(seeds, key=lambda k: (['ko', 'dose1', 'full'].index(seeds[k]['arm']), seeds[k]['seed']))]
    for r, k in enumerate(rows):
        v = seeds[k]
        for c, f in enumerate(fams):
            frac = v['per_family'][f] / v['n_family'][f]
            acq = f in v['acquired']
            b.add_patch(plt.Rectangle((c - 0.45, r - 0.45), 0.9, 0.9, color=col[v['arm']] if acq else '#f0efec', lw=0))
            b.text(c, r, f"{v['per_family'][f]}", ha='center', va='center', fontsize=7, color=SURF if acq else INK2)
    b.set_xlim(-0.6, len(fams) - 0.4); b.set_ylim(len(rows) - 0.4, -0.6)
    nfam = next(iter(seeds.values()))['n_family']
    b.set_xticks(range(len(fams))); b.set_xticklabels([f.replace('_', ' ').replace('demorgan nand to or', 'De Morgan') + f' ({nfam[f]})' for f in fams], rotation=25, ha='right', fontsize=8)
    b.set_yticks(range(len(rows))); b.set_yticklabels([f"{lab[seeds[k]['arm']].split(' (')[0]} s{seeds[k]['seed']}" for k in rows], fontsize=8)
    b.grid(False)
    b.set_title('(b) held-out members solved; filled = family acquired (≥ 50 %)', loc='left', fontsize=9)
    fig.text(0.01, -0.04, 'Plain sampling, k 256, T 0.8; Lean alone. 9.56 M ALiBiGPT, lean_staten, from scratch; T1 expert iteration, 16 rounds. '
             'Primary test (≥ 1 family acquired), full 6 / 6 vs knockout 0 / 6: one-sided Boschloo p = 2.4 × 10⁻⁴.', fontsize=7.5, color=INK2)
    fig.tight_layout()
    save(fig, 'coe_endpoint')


if __name__ == '__main__':
    {'estimator': estimator, 'budget': budget, 'rounds': rounds, 'endpoint': endpoint}[sys.argv[1]]()
