#!/usr/bin/env python3
"""Figures for run kalmar-complexity (system python3 with matplotlib).

  python3 kalmar_complexity/figures.py   # -> figures/kalmar_complexity.png, figures/kalmar_complexity_q4.png,
                                         #    figures/kalmar_complexity_b2.png (if B2 results exist)
Palette: the dataviz reference categorical slots 1-4 in fixed order (#2a78d6 blue, #eb6834 orange, #1baf7a aqua,
#eda100 yellow), validated light-mode on #fcfcfb (all checks pass; aqua / yellow < 3:1 contrast, so their marks
carry direct labels and every number is also in numbers.md).
"""
import collections, glob, gzip, json, math, os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
A = lambda p: os.path.join(ROOT, p)
BLUE, ORANGE, AQUA, YELLOW = '#2a78d6', '#eb6834', '#1baf7a', '#eda100'
GRAY, INK, INK2, SURF = '#9a9a96', '#1f1f1e', '#5f5e59', '#fcfcfb'
plt.rcParams.update({'font.size': 9, 'axes.edgecolor': '#c9c8c1', 'axes.labelcolor': INK2, 'xtick.color': INK2,
                     'ytick.color': INK2, 'axes.titlesize': 10, 'axes.titleweight': 'bold', 'figure.facecolor': SURF,
                     'axes.facecolor': SURF, 'savefig.facecolor': SURF, 'axes.spines.top': False,
                     'axes.spines.right': False, 'grid.color': '#e6e5df', 'grid.linewidth': 0.6})
SHORT = {'pr': 'premise line', 'lem': 'excluded middle', 'split': 'split', 'efq': 'ex falso', 'close': 'close box',
         'end': 'end', 'leaf:and+': '∧ true', 'leaf:and-': '∧ false', 'leaf:or+': '∨ true', 'leaf:or-': '∨ false',
         'leaf:imp+B': '→, B true', 'leaf:imp+A': '→, A false', 'leaf:imp-': '→ false', 'leaf:not+': '¬¬A',
         'leaf:bot-': '¬⊥'}


def program_lengths(ax3, axl):
    py = json.load(open(A('artifacts/kc/python_sizes.json')))
    blc = json.load(open(A('kalmar_complexity/programs/blc/results.json')))['programs']
    rasp = json.load(open(A('kalmar_complexity/programs/rasp/results.json')))
    rr = {r['task']: r for r in rasp['calibration']['rows']}
    items = ['copy', 'reverse', 'parity', 'sort', 'addition', 'eval', 'taut', 'Kalmár tt', 'Kalmár sl']
    pyv = {'copy': py['calib copy'], 'reverse': py['calib reverse'], 'parity': py['calib parity_nb'],
           'sort': py['calib sort_nb'], 'addition': py['calib add_nb'], 'eval': py['calib eval'], 'taut': py['calib taut'],
           'Kalmár tt': py['K-tt algorithm'], 'Kalmár sl': py['K-sl algorithm']}
    pyv = {k: v['deflate_bytes'] * 8 for k, v in pyv.items()}
    bl = {'copy': 'calib copy', 'reverse': 'calib reverse', 'parity': 'calib parity', 'sort': 'calib sort',
          'addition': 'calib add', 'eval': 'calib eval', 'taut': 'calib taut', 'Kalmár tt': 'K-tt algorithm',
          'Kalmár sl': 'K-sl algorithm'}
    blv = {k: blc[v]['blc_bits'] for k, v in bl.items()}
    rk = {'copy': 'copy', 'reverse': 'reverse', 'parity': 'parity_sp', 'sort': 'sort_rep',
          'addition': 'addition', 'eval': 'eval', 'taut': 'taut'}
    rv = {}
    for k, t in rk.items():
        m = [r for name, r in rr.items() if name.startswith(t)]
        if m:
            rv[k] = m[0]['ops']
    rv['Kalmár sl'] = rasp['decision']['ops']
    panels = [(ax3[0], pyv, 'Python, DEFLATE (bits)'), (ax3[1], blv, 'binary λ-calculus (bits)'),
              (ax3[2], rv, 'RASP-L (primitive ops)')]
    for ax, vals, title in panels:
        ys = [i for i, k in enumerate(items) if k in vals]
        xs = [vals[items[i]] for i in ys]
        cols = [BLUE if items[i].startswith('Kalmár') else GRAY for i in ys]
        ax.barh(ys, xs, height=0.62, color=cols, edgecolor=SURF, linewidth=2)
        for y, x in zip(ys, xs):
            ax.text(x * 1.12, y, f'{x:,}', va='center', ha='left', fontsize=7.5, color=INK2)
        ax.set_xscale('log')
        ax.set_xlim(2, max(xs) * 12)
        ax.set_yticks(range(len(items)))
        ax.set_yticklabels(items if ax is ax3[0] else [''] * len(items))
        ax.set_title(title, loc='left', fontsize=9)
        ax.grid(axis='x')
        ax.set_axisbelow(True)
        if 'Kalmár tt' not in vals:
            ax.text(3, items.index('Kalmár tt'), 'per-step policy only (sl)', va='center', fontsize=7, color=INK2)
    ax3[0].text(0, 1.13, 'A  Program length: Kalmár is the largest item in every language', transform=ax3[0].transAxes,
                fontsize=10, fontweight='bold', color=INK)
    # bits ladder
    b1 = json.load(open(A('artifacts/kc/b1_preq.json')))
    kd = [b1[f'KAL-D s{s}'] for s in range(3)]
    ct = [b1[f'control s{s}'] for s in range(3)]
    b2s = json.load(open(A('artifacts/kc/b2_summary.json'))) if os.path.exists(A('artifacts/kc/b2_summary.json')) else {}
    rows = [('decision tree over 21 state features', 626, GRAY),
            ('Kalmár sl algorithm, binary λ-calculus', blc['K-sl algorithm']['blc_bits'], BLUE),
            ('... + parse + render, binary λ-calculus', blc['K-sl parse + algorithm + rendering']['blc_bits'], BLUE),
            ('per-step policy, Python DEFLATE', py['K-sl per-step policy (state -> lean_seq action)']['deflate_bytes'] * 8, BLUE)]
    for name, lab in (('kal_S_s0', 'absorbed (EDL), 0.4 M model, 16k theorems (B2)'),
                      ('kal_M_s0', 'absorbed (EDL), 3.2 M model, 16k theorems (B2)'),
                      ('kal_L_s0', 'absorbed (EDL), 9.6 M model, 8k theorems (B2)')):
        if name in b2s:
            rows.append((lab, b2s[name]['summary']['EDL_bits'], ORANGE))
    rows += [('K12 control: absorbed (EDL), first epoch (B1)', float(np.mean([c['EDL_bits']['b_final_val'] for c in ct])), AQUA),
             ('KAL-D: absorbed (EDL), first epoch (B1)', float(np.mean([k['EDL_bits']['b_final_val'] for k in kd])), ORANGE),
             ('KAL-D: prequential code, first epoch (B1)', float(np.mean([k['L_preq_bits'] for k in kd])), ORANGE)]
    ys = np.arange(len(rows))[::-1]
    axl.barh(ys, [r[1] for r in rows], color=[r[2] for r in rows], height=0.62, edgecolor=SURF, linewidth=2)
    for y, (lab, v, c) in zip(ys, rows):
        if v < 1e5:
            lab_v = f'{v:,.0f}'
        else:
            e = int(math.floor(math.log10(v)))
            lab_v = rf'${v / 10 ** e:.1f}\times10^{{{e}}}$'
        axl.text(v * 1.15, y, lab_v, va='center', fontsize=7.5, color=INK2)
    axl.set_yticks(ys)
    axl.set_yticklabels([r[0] for r in rows], fontsize=8)
    axl.set_xscale('log')
    axl.set_xlim(200, 3e8)
    axl.axvline(9_560_832, color=INK2, lw=1, ls=(0, (3, 3)))
    axl.text(9_560_832 * 1.12, ys[0] + 0.1, '1 bit per KAL-D parameter', fontsize=7, color=INK2, va='center')
    axl.set_xlabel('bits (log scale)')
    axl.grid(axis='x')
    axl.set_axisbelow(True)
    axl.text(0, 1.03, 'B  Program bits vs bits the network absorbs (B1: 3-seed means; EDL residual = final held-out loss)',
             transform=axl.transAxes, fontsize=10, fontweight='bold', color=INK)


def fig_main():
    fig = plt.figure(figsize=(11, 8.2))
    gs = fig.add_gridspec(2, 3, height_ratios=[1.05, 1.15], hspace=0.42, wspace=0.08, left=0.27, right=0.97,
                          top=0.92, bottom=0.07)
    ax3 = [fig.add_subplot(gs[0, i]) for i in range(3)]
    axl = fig.add_subplot(gs[1, :])
    program_lengths(ax3, axl)
    fig.savefig(A('figures/kalmar_complexity.png'), dpi=160)
    plt.close(fig)


def fig_q4():
    R = json.load(open(A('artifacts/kc/q4/q4_results.json')))
    types, P, O = R['types'], R['predictors'], R['outcomes']
    err = O['kalD_mean']
    sp = R['spearman']
    fig, axs = plt.subplots(1, 4, figsize=(13, 3.9), gridspec_kw={'wspace': 0.32, 'left': 0.05, 'right': 0.98,
                                                                   'top': 0.80, 'bottom': 0.16})
    for ax, k, xl in ((axs[0], 'rasp_eff_depth', 'RASP-L attention depth of the decision'),
                      (axs[1], 'explored', 'in-scope lookups the choice needs'),
                      (axs[2], 'py_bytes', 'bytes of the Python code that emits it')):
        x = [P[t][k] for t in types]
        y = [100 * err[t] for t in types]
        lo = [100 * min(O[f'kalD_s{s}'][t] for s in range(3)) for t in types]
        hi = [100 * max(O[f'kalD_s{s}'][t] for s in range(3)) for t in types]
        ax.vlines(x, lo, hi, color=BLUE, alpha=0.35, lw=2)
        ax.scatter(x, y, s=34, color=BLUE, edgecolor=SURF, linewidth=1.5, zorder=3)
        off = {'leaf:or+': (-40, 6), 'leaf:bot-': (6, -10), 'leaf:and+': (5, 2), 'leaf:imp+B': (5, 2),
               'leaf:imp+A': (5, 3), 'pr': (5, 2), 'split': (5, 3), 'lem': (-62, 9) if k == 'py_bytes' else (5, -9)}
        for t, xi, yi in zip(types, x, y):
            if t in off:
                ax.annotate(SHORT.get(t, t), (xi, yi), xytext=off[t], textcoords='offset points', fontsize=7, color=INK2)
        r = sp[k]['kalD_mean']
        ax.set_title(f'ρ = {r["rho"]:+.2f} (p {r["p"]:.3f})', loc='left', fontsize=9)
        ax.set_xlabel(xl)
        ax.grid(True)
        ax.set_axisbelow(True)
    axs[0].set_ylabel('KAL-D teacher-forced error, %')
    # within type: error vs lookups, binned, for the four largest leaf types
    S = json.load(gzip.open(A('artifacts/kc/q4/states_tf1200.json.gz'), 'rt'))
    err_s = []
    for m in ('kalD_s0', 'kalD_s1', 'kalD_s2'):
        d = json.loads(os.popen(f"git -C {ROOT} show HEAD:artifacts/kalmar/tf/{m}__tf1200.json").read())
        err_s.append(np.array([c == '0' for row in d['rows'] for c in row['agree']], float))
    e = np.mean(err_s, 0)
    ax = axs[3]
    for t, c in (('leaf:imp+B', BLUE), ('leaf:not+', ORANGE), ('leaf:or+', AQUA), ('leaf:and-', YELLOW)):
        idx = [i for i, s in enumerate(S) if s['tag'] == t and s['explored'] >= 1]   # leaf-frame steps only
        by = collections.defaultdict(list)
        for i in idx:
            by[min(S[i]['explored'], 6)].append(e[i])
        xs = [k for k in sorted(by) if len(by[k]) >= 40]
        ys = [100 * np.mean(by[k]) for k in xs]
        ax.plot(xs, ys, color=c, lw=2, marker='o', ms=4, mec=SURF)
        ax.annotate(SHORT[t], (xs[-1], ys[-1]), xytext=(4, 0), textcoords='offset points', fontsize=7, color=INK2,
                    va='center')
    ax.set_xlabel('in-scope lookups (leaf-frame steps; 6 = 6+)')
    ax.set_ylabel('error, %')
    ax.set_title('within a step type', loc='left', fontsize=9)
    ax.grid(True)
    ax.set_axisbelow(True)
    ax.set_xlim(0.6, 7.4)
    ax.set_xticks(range(1, 7))
    fig.text(0.05, 0.93, 'Where KAL-D fails: per-step computational demand predicts it, program length does not '
             '(15 step types, tf1200; bars = seed range)', fontsize=10, fontweight='bold', color=INK)
    fig.savefig(A('figures/kalmar_complexity_q4.png'), dpi=160)
    plt.close(fig)


def fig_b2():
    runs = {os.path.basename(f)[:-5]: json.load(open(f)) for f in sorted(glob.glob(A('artifacts/kc/b2/*.json')))}
    if not runs:
        return
    fig, axs = plt.subplots(1, 2, figsize=(11, 3.8), gridspec_kw={'wspace': 0.25, 'left': 0.07, 'right': 0.98,
                                                                   'top': 0.82, 'bottom': 0.15})
    style = {'kal_S_s0': (BLUE, ':', 'Kalmár, S 0.4 M'), 'kal_M_s0': (BLUE, '--', 'Kalmár, M 3.2 M'),
             'kal_L_s0': (BLUE, '-', 'Kalmár, L 9.6 M'), 'v2_k12_S_s0': (ORANGE, ':', 'K12, S'),
             'v2_k12_M_s0': (ORANGE, '--', 'K12, M'), 'v2_k12_L_s0': (ORANGE, '-', 'K12, L'),
             'v2_eval_S_s0': (AQUA, ':', 'eval, S'), 'v2_eval_M_s0': (AQUA, '--', 'eval, M'),
             'v2_eval_L_s0': (AQUA, '-', 'eval, L')}
    for name, (c, ls, lab) in style.items():
        R = runs.get(name)
        if not R or len(R['blocks']) < 2:
            continue
        bl = [b for b in R['blocks'][1:] if not b.get('asymptote_block')]
        x = [b['block'][1] for b in bl]
        y = [b['bits'] / b['loss_tokens'] for b in bl]
        axs[0].plot(x, y, color=c, ls=ls, lw=2, label=lab)
        # cumulative prequential bits per theorem coded so far
        cum, cx, cy = R['blocks'][0]['bits'], [R['blocks'][0]['block'][1]], [R['blocks'][0]['bits']]
        for b in bl:
            cum += b['bits']; cx.append(b['block'][1]); cy.append(cum)
        axs[1].plot(cx, cy, color=c, ls=ls, lw=2, label=lab)
    for ax in axs:
        ax.set_xscale('log'); ax.set_yscale('log'); ax.grid(True); ax.set_axisbelow(True)
        ax.set_xlabel('theorems coded (end of block)')
    axs[0].set_ylabel('code, bits per loss token')
    axs[1].set_ylabel('cumulative prequential code, bits')
    axs[1].legend(fontsize=7, frameon=False, ncol=3, loc='upper left')
    axs[0].set_title('per-block code (model trained on all earlier blocks)', loc='left', fontsize=9)
    axs[1].set_title('cumulative code (first block at the uniform code)', loc='left', fontsize=9)
    fig.text(0.07, 0.92, 'B2: block-wise prequential code of three tasks under three model sizes (AdamW + early stopping)',
             fontsize=10, fontweight='bold', color=INK)
    fig.savefig(A('figures/kalmar_complexity_b2.png'), dpi=160)
    plt.close(fig)


if __name__ == '__main__':
    fig_main()
    fig_q4()
    fig_b2()
    print('figures written')
