#!/usr/bin/env python3
"""create-or-elicit: paper figures (vector PDF + 200-dpi PNG in figures/).  Palette: the dataviz reference instance
(validated: categorical slots 1-3 pass CVD / normal-vision checks on the light surface; aqua and the yellow slot sit below
3:1 contrast, so every series is also direct-labelled or in the legend, and every figure has a table in the write-up).

  python3 coe/coe_figures.py estimator      # figures/coe_estimator.{pdf,png}   (Phase 0.1)
  python3 coe/coe_figures.py budget         # figures/coe_budget.{pdf,png}      (Phase 0.2)
  python3 coe/coe_figures.py phase2         # figures/coe_phase2.{pdf,png}      (Phase 2, 2b)
  python3 coe/coe_figures.py rounds         # figures/coe_rounds.{pdf,png}      (Phase 1, per round; dose; knockout s1 extension)
  python3 coe/coe_figures.py endpoint       # figures/coe_endpoint.{pdf,png}    (Phase 1 r16 endpoint; dose)
  python3 coe/coe_figures.py logp           # figures/coe_logp.{pdf,png}        (log p of known sigma proofs along the ladders)
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
        elif b.startswith('la_dose1_s'):
            arm, seed = '1 % dose', int(b[len('la_dose1_s'):-5])
        else:
            continue
        d = json.load(open(fn))
        rs = sorted(int(r) for r in d['per_round'])
        tgt = [d['per_round'][str(r)]['sigma_targets_cum'] for r in rs]
        st = d.get('sigma_subtypes_by_round', {})
        free = [sum(v for k, v in st.get(str(r), {}).items() if k and k.startswith('pos_free')) for r in rs]
        out.append((arm, seed, rs, tgt, free))
    return out


def rounds():
    ser = _rounds_series()
    col = {'full': SER[0], 'knockout': SER[1], '1 % dose': SER[2]}
    fig, (a, b) = plt.subplots(1, 2, figsize=(9.6, 3.8))
    seen = set()
    last = 16
    for arm, seed, rs, tgt, free in ser:
        n = sum(1 for x in ser if x[0] == arm)
        lab = None if arm in seen else f"{arm} ({n} seed{'s' if n > 1 else ''})"
        seen.add(arm)
        k = [i for i, r in enumerate(rs) if r <= 16]
        a.plot([rs[i] for i in k], [tgt[i] for i in k], color=col[arm], lw=1.6, alpha=0.9, label=lab, marker='o', ms=3)
        b.plot([rs[i] for i in k], [free[i] + 0.5 for i in k], color=col[arm], lw=1.6, alpha=0.9, label=lab, marker='o', ms=3)
        x = [i for i, r in enumerate(rs) if r >= 16]
        if len(x) > 1:                      # knockout s1's exploratory extension (Addendum 6), dashed
            last = max(last, rs[x[-1]])
            a.plot([rs[i] for i in x], [tgt[i] for i in x], color=col[arm], lw=1.4, ls='--', marker='o', ms=3, mfc=SURF)
            b.plot([rs[i] for i in x], [free[i] + 0.5 for i in x], color=col[arm], lw=1.4, ls='--', marker='o', ms=3, mfc=SURF)
            b.text(rs[x[-1]], free[x[-1]] * 1.6 + 0.5, f'{arm} s{seed}', color=INK2, fontsize=7.5, ha='right')
            a.text(rs[x[-1]], tgt[x[-1]] + 5, f'{arm} s{seed}', color=INK2, fontsize=7.5, ha='right')
    for ax in (a, b):
        ax.set_xlim(0.5, last + 0.5)
        ax.set_xticks([1] + list(range(4, last + 1, 4)))
        if last > 16:
            ax.axvline(16.5, color=MUTED, lw=0.8, ls=':')
    a.set_xlabel('EI round'); a.set_ylabel('strict σ-covered training targets solved (of 123)')
    a.set_title('(a) classical targets that need σ', loc='left'); a.set_ylim(-3, 125)
    a.legend(loc='upper left', fontsize=8)
    b.set_yscale('log'); b.set_xlabel('EI round'); b.set_ylabel('accepted proofs with free positive σ (+0.5)')
    b.set_title('(b) proofs that build ¬¬G for a goal G the theorem never negates', loc='left', fontsize=9)
    fig.text(0.01, -0.03, 'Full: K12 bases s0–s5 (s0–s2 trajectory + rl-continue, s3–s5 this run); knockout: K12⁻ (σ removed) s0–s5; 1 % dose: '
             'K12⁻ + 1 % σ records, s0–s2. 9.56 M ALiBiGPT, lean_staten, T1 EI k 32; Lean alone. (b) counts every route (NEGI, IMPI, other); '
             'per round, not cumulative.\nDashed: knockout s1\'s exploratory extension past the pre-registered 16 rounds (Addendum 6).', fontsize=7.5, color=INK2)
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
    fig.text(0.01, -0.06, 'Plain sampling, k 256, T 0.8; Lean alone. 9.56 M ALiBiGPT, lean_staten, from scratch; T1 expert iteration, 16 rounds. '
             'Pre-registered test (≥ 1 family acquired): full 6 / 6 vs knockout 0 / 6,\none-sided Boschloo p = 2.4 × 10⁻⁴. '
             'Exploratory: 1 % dose 3 / 3 vs knockout 0 / 6, p = 0.0033. Full s0–s2 are trajectory\'s seeds (r1–r8 on RTX A6000); '
             'the dose arm\'s 1,550 σ records replace refill records of K12⁻.', fontsize=7.5, color=INK2)
    fig.tight_layout()
    save(fig, 'coe_endpoint')


def phase2():
    P = os.path.join(ROOT, 'artifacts/coe/power')
    rows = [('pilot, development (32)', 'pilot_a4_pend_s0', None, 'pilot_plainT0.8_pend_s0', 'pilot_plainT1.0_pend_s0'),
            ('full s0, solved rarely (17)', 'p2b_pc_a4', 'p2b_pc_a1.5', 'p2b_pc_plainT0.8', 'p2b_pc_plainT1.0'),
            ('full s0, compute-matched r8 set (33)', 'p2_full_s0_a4', 'p2_full_s0_a2', 'p2_full_s0_plainT0.8', 'p2_full_s0_plainT1.0'),
            ('full s1, compute-matched r8 set (27)', 'p2_full_s1_a4', 'p2_full_s1_a2', 'p2_full_s1_plainT0.8', 'p2_full_s1_plainT1.0'),
            ('knockout s0, strict σ members (106)', 'p2_ko_s0_a4', 'p2_ko_s0_a2', 'p2_ko_s0_plainT0.8', 'p2_ko_s0_plainT1.0'),
            ('knockout s1, strict σ members (106)', 'p2_ko_s1_a4', 'p2_ko_s1_a2', 'p2_ko_s1_plainT0.8', 'p2_ko_s1_plainT1.0')]
    kinds = [('power, α 4', SER[1], 'o', True), ('power, α 2 (1.5 on the 17)', SER[1], '^', False),
             ('plain, T 0.8', SER[0], 's', True), ('plain, T 1.0', SER[0], 'D', False)]
    fig, ax = plt.subplots(figsize=(8.6, 3.4))
    for r, (lab, *fs) in enumerate(rows):
        txt = []
        for j, f in enumerate(fs):
            if f is None:
                txt.append('–'); continue
            d = json.load(open(os.path.join(P, f + '.json')))
            n, k = d['n_theorems'], d['solved']
            name, c, m, filled = kinds[j]
            ax.plot([k / n], [r + (j - 1.5) * 0.12], m, ms=7, color=c, mfc=c if filled else SURF, mec=c, mew=1.4,
                    label=name if r == 2 else None, ls='none')
            txt.append(f'{k}/{n}')
        for j, t in enumerate(txt):
            ax.text(1.03 + 0.12 * j, r, t, va='center', fontsize=8, color=INK2, transform=ax.get_yaxis_transform())
    for j, h in enumerate(('α 4', 'α 2', 'T 0.8', 'T 1.0')):
        ax.text(1.03 + 0.12 * j, -0.75, h, va='center', fontsize=7.5, color=MUTED, transform=ax.get_yaxis_transform())
    ax.set_yticks(range(len(rows))); ax.set_yticklabels([x[0] for x in rows], fontsize=8)
    ax.set_ylim(len(rows) - 0.5, -1.0); ax.set_xlim(-0.03, 1.0)
    ax.set_xlabel('fraction of the set solved (same decoded tokens per theorem for all four samplers)')
    ax.legend(loc='lower right', fontsize=7.5, ncol=1)
    ax.set_title('Power sampling the base (p^α) vs plain sampling at matched tokens', loc='left')
    fig.text(0.01, -0.05, 'Bases (pend): full s0 / s1 = best-cap12 s0 / s1; knockout = K12⁻ s0 / s1. Power: 32 chains per theorem (16 on the pilot), '
             'blocks of 4 steps, 8 MH steps per block. 9.56 M ALiBiGPT, lean_staten; Lean alone.', fontsize=7.5, color=INK2)
    fig.tight_layout()
    save(fig, 'coe_phase2')


def logp():
    import glob
    col = {'full': SER[0], 'ko': SER[1], 'dose1': SER[2]}
    lab = {'full': 'full', 'ko': 'knockout', 'dose1': '1 % dose'}
    fig, ax = plt.subplots(figsize=(5.6, 3.6))
    seen = set()
    for fn in sorted(glob.glob(os.path.join(ROOT, 'artifacts/coe/score/rounds_*/summary.json'))):
        name = fn.split('/')[-2][len('rounds_'):]
        arm = name.rsplit('_s', 1)[0]
        ck = json.load(open(fn))['ckpts']
        pts = sorted((0 if k == 'pend' else int(k[1:]), v['heldout']['best_median']) for k, v in ck.items())
        ax.plot([x for x, _ in pts], [y for _, y in pts], color=col[arm], marker='o', ms=4, lw=1.6, alpha=0.9,
                label=None if arm in seen else lab[arm])
        seen.add(arm)
    ax.set_xticks([0, 4, 8, 12, 16]); ax.set_xticklabels(['pend', 'r4', 'r8', 'r12', 'r16'])
    ax.set_xlabel('checkpoint along the ladder'); ax.set_ylabel('log p of the best known σ proof (nats; median)')
    ax.set_title('Does RL move the model toward σ proofs?', loc='left')
    ax.legend(loc='center left', bbox_to_anchor=(1.01, 0.5), fontsize=8)
    fig.text(0.01, -0.06, 'Teacher-forced log p at T 0.8, one name base (subtract ln 33 for a lower bound), of 9,501 known Lean-accepted\n'
             'proofs of the strict σ-covered held-out members (from the old full ladders); median over 101 members of each\n'
             "member's best known proof. One line per ladder. 9.56 M ALiBiGPT, lean_staten.", fontsize=7.5, color=INK2)
    fig.tight_layout()
    save(fig, 'coe_logp')


if __name__ == '__main__':
    {'estimator': estimator, 'budget': budget, 'rounds': rounds, 'endpoint': endpoint, 'phase2': phase2, 'logp': logp}[sys.argv[1]]()
