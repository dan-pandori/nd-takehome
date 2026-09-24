#!/usr/bin/env python3
"""cap-horizon figures, from artifacts/kh/summary.json (kh_analysis.py).

  python3 kh_figures.py

figures/cap_horizon_horizon.png   the horizon against the cap: max accepted pruned length on
                                  targets_reductio_req (both Stage-1 seeds) and ladder L* (T1
                                  beside frozen, Stage-1 seed 0), with the pre-registered
                                  predictions and the L* censoring ceiling drawn.
figures/cap_horizon_readiness.png the readiness panel per arm.

Colour: the dataviz skill's validated default categorical palette, slots taken in fixed order and
never cycled; each panel carries its own legend so identity is never colour-alone.  (The skill's
validate_palette.js could not be run -- no node on this VPS -- so the palette values are used
exactly as the reference instance specifies them, unmodified.)  Light surface only: these are PNGs
for a markdown write-up, not an interactive chart.
"""
import json, os, sys
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

S1, S2, S3, S4 = '#2a78d6', '#eb6834', '#1baf7a', '#eda100'   # categorical slots 1-4, fixed order
INK, INK2, MUTED, SURF = '#0b0b0b', '#52514e', '#b4b3ae', '#fcfcfb'
ORDER = ['K6', 'K8flat', 'K8add', 'K10', 'K12', 'K14']

d = json.load(open('artifacts/kh/summary.json'))
rows = {(r['arm'], r['stage1_seed']): r for r in d['rows']}
arms = [a for a in ORDER if (a, 0) in rows]
cap = {a: rows[(a, 0)]['cap'] for a in arms}
# two arms share cap 8 (K8flat and K8add); give them distinct x positions so the curves read as
# points per ARM, not as a vertical jump at one cap
_dupe = [a for a in arms if sum(1 for b in arms if cap[b] == cap[a]) > 1]
xpos = {a: cap[a] + (-0.22 if a == _dupe[0] else 0.22) if a in _dupe else cap[a] for a in arms}


def val(arm, seed, *path):
    r = rows.get((arm, seed))
    for p in path:
        if r is None:
            return None
        r = r.get(p) if isinstance(r, dict) else None
    return r


def axstyle(ax, xlabel, ylabel, title):
    ax.set_facecolor(SURF)
    ax.grid(True, axis='y', color=MUTED, lw=0.6, alpha=0.5)
    ax.set_axisbelow(True)
    for s in ('top', 'right'):
        ax.spines[s].set_visible(False)
    for s in ('left', 'bottom'):
        ax.spines[s].set_color(MUTED)
    ax.tick_params(colors=INK2, labelsize=8)
    ax.set_xlabel(xlabel, color=INK2, fontsize=9)
    ax.set_ylabel(ylabel, color=INK2, fontsize=9)
    ax.set_title(title, color=INK, fontsize=10, loc='left')


# ---------------------------------------------------------------- figure 1
fig, (a1, a2) = plt.subplots(1, 2, figsize=(11.5, 4.4), facecolor=SURF)
caps = sorted({cap[a] for a in arms})

# Panel A: the horizon is POOL-SPECIFIC.  On targets_reductio_req, where the target needs the long
# proof, the longest accepted proof sits at about the cap; on pools where a longer proof is merely
# permitted the same models run 3-8 lines above their own cap -- including cap 6.
SER = [('redreq', S1, 'targets_reductio_req (pass@2,000)', ('redreq', 'max_pruned_len')),
       ('d3req', S2, 'depth3_req (pass@2,000)', ('d3req', 'max_pruned_len')),
       ('ladder', S3, 'ladder transfer, rung T1 (8 x 32)', ('ladder_T1', 'max_pruned_len'))]
for _, col, lab, path in SER:
    xs, ys = [], []
    for a in arms:
        vs = [val(a, s_, *path) for s_ in (0, 1)]
        vs = [v for v in vs if v]
        if vs:
            xs.append(xpos[a]); ys.append(max(vs))
    a1.plot(xs, ys, 'o-', color=col, lw=2, ms=8, label=lab, zorder=3,
            markeredgecolor=SURF, markeredgewidth=2)
a1.plot(caps, caps, '--', color=MUTED, lw=1.5, zorder=1, label='length = cap')
for a in arms:
    v = max(v for v in (val(a, 0, 'redreq', 'max_pruned_len'), val(a, 1, 'redreq', 'max_pruned_len')) if v)
    a1.annotate(a, (xpos[a], v), textcoords='offset points',
                xytext=(0, -16) if a != 'K8flat' else (-6, 10), ha='center',
                fontsize=7.5, color=INK2)
axstyle(a1, 'training cap (pruned lines)', 'max accepted pruned length (best of 2 seeds)',
        'A · the horizon is pool-specific: at the cap where the proof is needed,\n    3-8 lines above it where a longer proof is merely allowed')
a1.legend(frameon=False, fontsize=8, labelcolor=INK2, loc='upper left')

for key, col, lab in (('ladder_T1', S1, 'ladder rung T1'), ('ladder_frozen', S2, 'frozen, equal attempts')):
    xs, ys = [], []
    for a in arms:
        v = val(a, 0, key, 'lstar')
        if v:
            xs.append(xpos[a]); ys.append(v)
    a2.plot(xs, ys, 'o-', color=col, lw=2, ms=8, label=lab, zorder=3,
            markeredgecolor=SURF, markeredgewidth=2)
a2.plot(caps, [min(c + 3, 14) for c in caps], '--', color=MUTED, lw=1.5, zorder=1,
        label='pre-registered: min(cap + 3, 14)')
ymax = 18
a2.axhspan(14.5, ymax, color=MUTED, alpha=0.35, zorder=0)
a2.annotate('not measurable — the transfer pool censors L* at 14\n(23 theorems at L_true ≥ 13, 10 at ≥ 14)',
            (caps[0], 15.1), fontsize=7.5, color=INK2, va='bottom')
for a in arms:
    v = val(a, 0, 'ladder_frozen', 'lstar')
    if v:
        a2.annotate(a, (xpos[a], v), textcoords='offset points', xytext=(0, -15), ha='center',
                    fontsize=7.5, color=INK2)
a2.set_ylim(6, ymax)
axstyle(a2, 'training cap (pruned lines)', 'transfer L*',
        'B · ladder L* (Stage-1 seed 0), frozen beside T1')
a2.legend(frameon=False, fontsize=8, labelcolor=INK2, loc='lower right')
fig.suptitle('cap-horizon — the proof-length horizon against the training cap  ·  3,214,336-parameter from-scratch model, lean_seq, Stage-1 6,000 steps',
             fontsize=9.5, color=INK2, x=0.01, ha='left')
fig.tight_layout(rect=(0, 0, 1, 0.94))
os.makedirs('figures', exist_ok=True)
fig.savefig('figures/cap_horizon_horizon.png', dpi=170, facecolor=SURF)
print('figures/cap_horizon_horizon.png')

# ---------------------------------------------------------------- figure 2
PANELS = [
    ('held-out greedy (cap-6 pool — OOD above cap 6)', lambda a, s: val(a, s, 'heldout', 'rate'), 'rate', 'greedy accuracy'),
    ('targets_reductio_req solved / 300', lambda a, s: val(a, s, 'redreq', 'solved'), 'seed', 'targets'),
    ('accepted redreq proofs ≥ 12 pruned lines', lambda a, s: val(a, s, 'redreq', 'ge12'), 'seed', 'distinct proofs'),
    ('redreq solved by REQUIRED length (min_lines_ub), seed 0', None, 'strata', 'targets solved'),
    ('ladder transfer solved / 2,285 (seed 0)', None, 'ladder', 'theorems'),
    ('ladder transfer solved at L_true ≥ 12 (seed 0)', None, 'ladder_ge12', 'theorems'),
]
fig, axs = plt.subplots(2, 3, figsize=(14, 7), facecolor=SURF)
x = range(len(arms))
w = 0.38
for ax, (title, f, kind, ylab) in zip(axs.ravel(), PANELS):
    if kind == 'rate':
        # a DOT plot, not bars: these are rates in a narrow band, and a bar chart would need a
        # truncated baseline to show the differences at all
        for i, (seed, col, lab) in enumerate(((0, S1, 'Stage-1 seed 0'), (1, S2, 'Stage-1 seed 1'))):
            vs = [f(a, seed) for a in arms]
            ax.plot(list(x), vs, 'o', color=col, ms=9, label=lab, markeredgecolor=SURF,
                    markeredgewidth=1.5, zorder=3)
        lo = min(v for a in arms for v in (f(a, 0), f(a, 1)) if v)
        hi = max(v for a in arms for v in (f(a, 0), f(a, 1)) if v)
        ax.set_ylim(lo - 0.02, hi + 0.035)
    elif kind == 'seed':
        for i, (seed, col, lab) in enumerate(((0, S1, 'Stage-1 seed 0'), (1, S2, 'Stage-1 seed 1'))):
            vs = [f(a, seed) or 0 for a in arms]
            ax.bar([j + (i - 0.5) * w for j in x], vs, w * 0.92, color=col, label=lab,
                   edgecolor=SURF, linewidth=1.2)
    elif kind == 'strata':
        ws = 0.2
        for i, (st, col) in enumerate((('7', S1), ('8', S2), ('9', S3), ('10', S4))):
            vs = [((val(a, 0, 'redreq', 'strata_solved') or {}).get(st) or [0, 0])[0] for a in arms]
            ax.bar([j + (i - 1.5) * ws for j in x], vs, ws * 0.9, color=col,
                   label=f'needs ≥ {st} lines', edgecolor=SURF, linewidth=1.0)
    else:
        key = 'transfer_solved'
        for i, (k, col, lab) in enumerate((('ladder_T1', S3, 'rung T1'), ('ladder_frozen', S4, 'frozen, equal attempts'))):
            if kind == 'ladder_ge12':
                vs = [int(((val(a, 0, k, 'ge_L_true') or {}).get('12')) or 0) for a in arms]
            else:
                vs = [val(a, 0, k, key) or 0 for a in arms]
            ax.bar([j + (i - 0.5) * w for j in x], vs, w * 0.92, color=col, label=lab,
                   edgecolor=SURF, linewidth=1.2)
    ax.set_xticks(list(x))
    ax.set_xticklabels([f'{a}\ncap {cap[a]}' for a in arms], fontsize=7.5)
    axstyle(ax, '', ylab, title)
    ax.legend(frameon=False, fontsize=7.5, labelcolor=INK2)
fig.suptitle('cap-horizon — readiness per arm  ·  3,214,336-parameter from-scratch lean_seq model trained at that arm’s cap\n'
             'K6 and K8flat are inherited (ds-composition C0 and A3)  ·  K8add’s set is 217,000 records, every other arm’s is 155,000',
             fontsize=8.5, color=INK2, x=0.01, ha='left')
fig.tight_layout(rect=(0, 0, 1, 0.93))
fig.savefig('figures/cap_horizon_readiness.png', dpi=170, facecolor=SURF)
print('figures/cap_horizon_readiness.png')
