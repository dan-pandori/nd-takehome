#!/usr/bin/env python3
"""Figures for run stage1-dynamics from artifacts/sd/summary.json (sd_analysis.py) ->
figures/sd_valloss.png   (a) validation loss per length bin and on the depth-3 slice over steps,
                             W (control set) vs F (fresh set) vs C, with the old `val2k` for contrast
figures/sd_traj.png      (b) Lean-alone held-out accuracy per length and on the depth-3 slice over
                             steps, one line per seed, with the decayed branches marked
figures/sd_proxy.png     (c) per-bin validation loss against per-bin accuracy across checkpoints, and
                             the same at a fixed step across seeds (the question that matters)
Categorical colours are the same dataviz reference palette slots, in the same fixed order, that
nf_figures.py and dsg_figures.py use (blue = the control set / arm W, orange = arm C, aqua = arm F);
identity is never colour-alone -- arms also differ in marker and dash, and seeds are labelled.
"""
import json, os, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

S = json.load(open('artifacts/sd/summary.json'))
Q, CELLS, CURVES = S['questions'], S['cells'], S['curves']
BLUE, ORANGE, AQUA = '#2a78d6', '#eb6834', '#1baf7a'
INK, MUTED, SURF, GRID = '#0b0b0b', '#52514e', '#fcfcfb', '#e6e5e0'
plt.rcParams.update({'font.size': 8.5, 'axes.edgecolor': '#c9c8c2', 'axes.labelcolor': MUTED, 'xtick.color': MUTED,
                     'ytick.color': MUTED, 'text.color': INK, 'axes.spines.top': False, 'axes.spines.right': False,
                     'figure.facecolor': SURF, 'axes.facecolor': SURF, 'savefig.facecolor': SURF})
os.makedirs('figures', exist_ok=True)
BINS = [('len2', '2-line'), ('len3', '3-line'), ('len4', '4-line'), ('len5', '5-line'),
        ('len6', '6-line'), ('depth3', 'depth-3 slice (500)'), ('nodepth3_len6', '6-line, no depth-3'),
        ('val2k', "the old `val2k` (lengths 2-3 only)")]


def curve(tag, key):
    c = CURVES.get(tag)
    if not c:
        return [], []
    xs, ys = [], []
    for s in c['steps']:
        v = s['val2k'] if key == 'val2k' else (s['val'] or {}).get(key)
        if v is not None:
            xs.append(s['step']); ys.append(v)
    return xs, ys


def band(ax, tags, key, color, label, dash=None):
    """median with a min-max band over the seeds present"""
    cs = [curve(t, key) for t in tags]
    cs = [c for c in cs if c[0]]
    if not cs:
        return
    grid = sorted(set(cs[0][0]).intersection(*[set(c[0]) for c in cs])) if len(cs) > 1 else cs[0][0]
    if not grid:
        return
    M = np.array([[dict(zip(*c))[g] for g in grid] for c in cs])
    ax.fill_between(grid, M.min(0), M.max(0), color=color, alpha=0.16, lw=0)
    ax.plot(grid, np.median(M, 0), color=color, lw=1.5, ls=dash or '-', label=f'{label} (n={len(cs)})')


# ---------------------------------------------------------------- (a) validation loss per bin
WT = [f'w_s{k}' for k in range(8)]
FT = [f'f_s{k}' for k in range(4)]
CT = [f'c_s{k}' for k in range(8)]
fig, axes = plt.subplots(2, 4, figsize=(13.4, 6.2), sharex=True)
for ax, (key, lab) in zip(axes.ravel(), BINS):
    band(ax, WT, key, BLUE, 'W  WSD 24k, control set')
    band(ax, FT, key, AQUA, 'F  WSD 24k, fresh set')
    band(ax, CT, key, ORANGE, 'C  cosine 6k, control set', dash=(0, (4, 2)))
    ax.axvline(6000, color='#c9c8c2', lw=0.7, zorder=0)
    ax.axvline(19200, color='#c9c8c2', lw=0.7, ls=':', zorder=0)
    ax.set_title(lab, fontsize=8.5, color=INK, loc='left')
    ax.set_yscale('log'); ax.grid(color=GRID, lw=0.6)
for ax in axes[1]:
    ax.set_xlabel('step')
for ax in axes[:, 0]:
    ax.set_ylabel('validation cross-entropy per proof token')
axes[0, 0].legend(frameon=False, fontsize=7.2, loc='upper right')
fig.suptitle('(a) Validation loss per length bin, whole 5,000-record held-out file — 3,214,336-parameter from-scratch '
             '`lean_seq` GPT, cap 6.  Solid line = median over seeds, band = min–max.\n'
             'Thin line at 6,000 steps = the recipe the project has been using; dotted at 19,200 = where W and F begin '
             'their linear decay.  `val2k` is the number every past curve in this project plotted.',
             fontsize=8.2, color=MUTED, x=0.008, ha='left', y=0.995)
fig.tight_layout(rect=(0, 0, 1, 0.92))
fig.savefig('figures/sd_valloss.png', dpi=170)
plt.close(fig)

# ---------------------------------------------------------------- (b) accuracy trajectories per seed
PANELS = [('all', 'held-out overall (5,000)'), ('len6', '6-line bin (1,000)'),
          ('depth3', 'depth-3 slice (500)'), ('nodepth3_len6', '6-line, no depth-3 (500)')]
fig, axes = plt.subplots(2, 4, figsize=(13.4, 6.4), sharex=True)
cmap = plt.get_cmap('viridis')
for row, (armt, armf, tag, col) in enumerate([('Wtraj', 'W', 'W  control set', BLUE),
                                              ('Ftraj', 'F', 'F  fresh set (572,759)', AQUA)]):
    seeds = sorted({c['seed'] for c in CELLS if c['arm'] == armt})
    for j, (key, lab) in enumerate(PANELS):
        ax = axes[row, j]
        for i, k in enumerate(seeds):
            pts = sorted([(c['step'], c[key]) for c in CELLS if c['arm'] == armt and c['seed'] == k and key in c])
            fin = [(c['step'], c[key]) for c in CELLS if c['arm'] == armf and c['seed'] == k and key in c]
            cc = cmap(0.08 + 0.84 * i / max(len(seeds) - 1, 1))
            if pts:
                ax.plot(*zip(*pts), color=cc, lw=1.0, marker='o', ms=2.2, label=f'seed {k}')
            if fin:
                ax.plot(*zip(*fin), color=cc, marker='*', ms=9, ls='')
        if row == 0:
            for arm, mk in (('W6k', 's'), ('W12k', 'D')):
                for i, k in enumerate(seeds):
                    c = next((c for c in CELLS if c['arm'] == arm and c['seed'] == k and key in c), None)
                    if c:
                        ax.plot(c['step'], c[key], marker=mk, ms=5, ls='', mfc='none',
                                mec=cmap(0.08 + 0.84 * i / max(len(seeds) - 1, 1)), mew=1.2)
        if key == 'depth3':
            ax.axhline(0.44, color=ORANGE, lw=0.9, ls=(0, (4, 2)))
            ax.text(400, 0.455, "NOISE_FLOOR.md's high-mode cut 0.44", fontsize=6.8, color=ORANGE)
        ax.axvline(6000, color='#c9c8c2', lw=0.7, zorder=0)
        ax.set_title(f'{tag} — {lab}', fontsize=8.2, color=INK, loc='left')
        ax.grid(color=GRID, lw=0.6); ax.set_ylim(-0.03, 1.03)
        if row == 1:
            ax.set_xlabel('step')
axes[0, 0].set_ylabel('Lean-alone greedy solve rate')
axes[1, 0].set_ylabel('Lean-alone greedy solve rate')
axes[0, 0].legend(frameon=False, fontsize=6.4, loc='lower right', ncol=2)
fig.suptitle('(b) Held-out greedy accuracy over training, one line per Stage-1 seed — judged by Lean alone.  '
             'Circles = the stable-phase trajectory (undecayed; W and F decay from 19,200).\n'
             'Hollow square = W-6k, hollow diamond = W-12k, star = the arm\'s own decayed final checkpoint.  '
             'The depth-3 slice is bimodal, so it is shown per seed and never as a mean.',
             fontsize=8.2, color=MUTED, x=0.008, ha='left', y=0.995)
fig.tight_layout(rect=(0, 0, 1, 0.92))
fig.savefig('figures/sd_traj.png', dpi=170)
plt.close(fig)

# ---------------------------------------------------------------- (c) is per-bin loss a proxy?
def vat(tag, step, key):
    xs, ys = curve(tag, key)
    d = dict(zip(xs, ys))
    return d.get(step)


fig, axes = plt.subplots(1, 3, figsize=(13.4, 4.3))
PAIRS = [('len6', 'len6', '6-line validation loss  vs  6-line accuracy'),
         ('depth3', 'depth3', 'depth-3 validation loss  vs  depth-3 accuracy'),
         ('val2k', 'len6', "the old `val2k`  vs  6-line accuracy")]
for ax, (vkey, akey, title) in zip(axes, PAIRS):
    for i, k in enumerate(range(8)):
        pts = []
        for c in CELLS:
            if c['arm'] in ('Wtraj', 'W') and c['seed'] == k and akey in c:
                v = vat(f'w_s{k}', c['step'], vkey)
                if v is not None:
                    pts.append((v, c[akey], c['step']))
        if pts:
            pts.sort(key=lambda t: t[2])
            cc = cmap(0.08 + 0.84 * i / 7)
            ax.plot([p[0] for p in pts], [p[1] for p in pts], color=cc, lw=0.8, marker='o', ms=2.4,
                    alpha=0.9, label=f'seed {k}' if ax is axes[0] else None)
            ax.plot(pts[-1][0], pts[-1][1], marker='*', ms=10, ls='', color=cc)
    key = f'trajectory' if False else None
    rho = (Q.get('Q5_proxy', {}).get('trajectory', {}).get(f'val_{vkey}_vs_acc_{akey}', {}) or {}).get('spearman_pooled')
    fx = (Q.get('Q5_proxy', {}).get('fixed_step_ranking', {}).get(f'step24000_val_{vkey}_vs_acc_{akey}', {}) or {})
    sub = f'pooled trajectory Spearman ρ = {rho:.3f}' if rho is not None else ''
    if fx.get('spearman') is not None:
        sub += f'\nacross the {fx["n_seeds"]} seeds at step 24,000 only: ρ = {fx["spearman"]:.3f}'
    ax.set_title(title, fontsize=8.5, color=INK, loc='left')
    ax.text(0.98, 0.04, sub, transform=ax.transAxes, ha='right', va='bottom', fontsize=7.4, color=MUTED)
    ax.set_xscale('log'); ax.grid(color=GRID, lw=0.6)
    ax.set_xlabel('validation cross-entropy per proof token')
axes[0].set_ylabel('Lean-alone greedy solve rate')
axes[0].legend(frameon=False, fontsize=6.6, loc='upper right', ncol=2)
fig.suptitle('(c) Does a validation loss rank models?  Each line is one seed of arm W walking from step 1,000 '
             '(top right, high loss) to step 24,000 (star).\nAlong a single run every loss tracks accuracy; the '
             'question that matters is whether it ranks different runs at the same step — the second ρ in each panel.',
             fontsize=8.2, color=MUTED, x=0.008, ha='left', y=0.995)
fig.tight_layout(rect=(0, 0, 1, 0.86))
fig.savefig('figures/sd_proxy.png', dpi=170)
plt.close(fig)
print('wrote figures/sd_valloss.png figures/sd_traj.png figures/sd_proxy.png')
