#!/usr/bin/env python3
"""Figures for run noise-floor from artifacts/nf/summary.json (nf_analysis.py) ->
figures/nf_cells.png (the eight null cells per quantity, with the control's published value marked)
and figures/nf_resolvable.png (the resolvable-difference table as a chart, with every standing
finding this run retests plotted against its own floor).
Categorical colours = the dataviz reference palette slots used by dsg_figures.py, in the same fixed order
(blue = null cells, orange = a standing finding below its floor, aqua = above it); identity is never
colour-alone: Stage-1 seed 0 is a circle and seed 1 a triangle, gap-closers are hollow diamonds, and
findings below the floor are additionally drawn hollow."""
import json, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

S = json.load(open('artifacts/nf/summary.json'))
F = S['floors']
BLUE, ORANGE, AQUA = '#2a78d6', '#eb6834', '#1baf7a'
INK, MUTED, SURF = '#0b0b0b', '#52514e', '#fcfcfb'
plt.rcParams.update({'font.size': 8.5, 'axes.edgecolor': '#c9c8c2', 'axes.labelcolor': MUTED, 'xtick.color': MUTED,
                     'ytick.color': MUTED, 'text.color': INK, 'axes.spines.top': False, 'axes.spines.right': False,
                     'figure.facecolor': SURF, 'axes.facecolor': SURF, 'savefig.facecolor': SURF})

# quantity -> (label, control's published value and the model it was measured on, extra hollow points)
# every published value is the C0 control of ds-generator / ds-composition: ckpts/lf/stage1_a1_seq_s{0,1}.pt,
# 3.3 M-parameter lean_seq GPT trained on data/p2/train_depth3_f0_a1.jsonl.
ROWS = [
    ('ladder_frozen_transfer_solved', 'frozen ladder, transfer solved / 2,285', [158, 114]),
    ('ladder_frozen_transfer_lstar', 'frozen ladder, transfer $L^*$', [9, 9]),
    ('cov_red_solved', '`targets_reductio_req` solved / 300', [31, 27]),
    ('cov_req8_solved', '`depth3_req` required@8 solved / 300', [165, 113]),
    ('cov_d3_solved', '`targets_depth3` solved / 1,000', [506, 423]),
    ('heldout_depth3_slice', 'held-out depth-3 slice (n = 500)', [0.488, 0.446]),
    ('heldout_len6', 'held-out greedy, 6-line bin', [0.686, 0.584]),
    ('heldout_overall', 'held-out greedy, overall', [0.9088, 0.8968]),
]

# ---------- figure 1: the eight null cells per quantity, as ratios to their own mean ----------
fig, ax = plt.subplots(figsize=(10.5, 4.6))
ylab = []
for i, (q, lab, ctrl) in enumerate(ROWS):
    f = F.get(q)
    if not f:
        continue
    y = len(ROWS) - i
    m = f['mean']
    vals = f['values']
    ax.hlines(y, f['min'] / m, f['max'] / m, color='#d7d6d0', lw=6, zorder=1)
    for k, v in vals.items():
        ax.plot(v / m, y, marker='o' if k.endswith('s0') else '^', ms=6, color=BLUE, mec=SURF, mew=0.6, zorder=3)
    for c in ctrl:
        ax.plot(c / m, y, marker='|', ms=15, color=ORANGE, mew=2.0, zorder=4)
    g = S['gap_closers'].get('la_frozen_dsg_g1_s0')
    if q == 'ladder_frozen_transfer_solved' and g:
        ax.plot(g['transfer_solved'] / m, y, marker='D', ms=6, mfc='none', mec=AQUA, mew=1.4, zorder=4)
        ax.plot(170 / m, y, marker='D', ms=6, mfc='none', mec=AQUA, mew=1.4, zorder=4)
    ylab.append((y, f'{lab}\nmean {m:.4g}, sd {f["sd"]:.3g}, max/min {f["max_over_min"]:.2f}×'))
ax.axvline(1.0, color='#c9c8c2', lw=0.8, zorder=0)
ax.set_yticks([y for y, _ in ylab]); ax.set_yticklabels([t for _, t in ylab], fontsize=7.5)
ax.set_xlabel('value ÷ mean of the eight null cells  (everything on this chart is noise by construction)')
ax.grid(axis='x', color='#e6e5e0', lw=0.6)
h = [plt.Line2D([], [], marker='o', ls='', color=BLUE, label='null cell, Stage-1 seed 0'),
     plt.Line2D([], [], marker='^', ls='', color=BLUE, label='null cell, Stage-1 seed 1'),
     plt.Line2D([], [], marker='|', ls='', color=ORANGE, mew=2, label="C0 control's published value (both seeds)"),
     plt.Line2D([], [], marker='D', ls='', mfc='none', mec=AQUA, label='ds-generator G1 (fifth independent draw)')]
ax.legend(handles=h, frameon=False, fontsize=7.5, loc='lower right')
fig.suptitle('noise-floor: four independent null pools × two Stage-1 seeds, same generator settings, same composition, same schedule',
             fontsize=10, x=0.01, ha='left')
fig.tight_layout(); fig.savefig('figures/nf_cells.png', dpi=160); plt.close(fig)

# ---------- figure 2: resolvable difference vs the standing findings ----------
# (quantity, finding label, observed effect as a fraction of the control value; pp quantities as a fraction too)
FINDINGS = [
    ('ladder_frozen_transfer_solved', 'ds-composition A3 cap-8 vs C0 (976 vs 158)', 976 / 158 - 1),
    ('ladder_frozen_transfer_solved', 'ds-generator G1 vs C0 s1 (170 vs 114)', 170 / 114 - 1),
    ('ladder_frozen_transfer_solved', 'ds-composition A1 vs C0, n = 1 (205 vs 158)', 205 / 158 - 1),
    ('ladder_frozen_transfer_solved', 'ds-composition A2 vs C0, n = 1 (111 vs 158)', 1 - 111 / 158),
    ('ladder_frozen_transfer_solved', 'ds-generator G2 vs C0 s1 (125 vs 114)', 125 / 114 - 1),
    ('cov_req8_solved', 'ds-generator G1 vs C0 s1 (259 vs 113)', 259 / 113 - 1),
    ('cov_red_solved', 'ds-composition A3 cap-8 vs C0 (54 vs 28)', 54 / 28 - 1),
    ('cov_red_solved', 'ds-composition A1 vs C0 (16 vs 28)', 1 - 16 / 28),
    ('heldout_overall', 'lean-format lean_seq vs token (0.909 vs 0.883)', 0.909 / 0.883 - 1),
    ('heldout_overall', 'ds-composition A1 vs C0 s0 (0.9172 vs 0.9088)', 0.9172 / 0.9088 - 1),
    ('heldout_len6', 'ds-composition A1 vs C0 s1 (0.840 vs 0.583)', 0.840 / 0.583 - 1),
    ('heldout_depth3_slice', 'ds-rendering R2 − C0 (0.661 vs 0.533)', 0.661 / 0.533 - 1),
    ('ladder_frozen_transfer_lstar', 'ds-composition A1 vs C0 $L^*$ (10 vs 9)', 10 / 9 - 1),
    ('ladder_frozen_transfer_lstar', 'ds-composition A3 cap-8 $L^*$ (11 vs 9)', 11 / 9 - 1),
]
qs = [q for q, _, _ in ROWS if q in F]
fig, ax = plt.subplots(figsize=(10.5, 4.8))
ypos = {q: len(qs) - i for i, q in enumerate(qs)}
for q in qs:
    f = F[q]
    frac = f['mdd_n2_frac_of_mean']
    ax.barh(ypos[q], 100 * frac, height=0.42, color='#e2e1db', edgecolor='#c9c8c2', lw=0.6, zorder=1)
    ax.text(100 * frac + 2, ypos[q], f'{100 * frac:.0f} %', va='center', fontsize=7.5, color=MUTED)
for q, lab, eff in FINDINGS:
    if q not in ypos:
        continue
    below = 100 * eff < 100 * F[q]['mdd_n2_frac_of_mean']
    ax.plot(100 * eff, ypos[q], marker='o', ms=7, mfc='none' if below else (AQUA if not below else 'none'),
            mec=ORANGE if below else AQUA, mew=1.6, zorder=3)
    ax.annotate(lab, (100 * eff, ypos[q]), textcoords='offset points', xytext=(7, 7 if eff > 0 else -12),
                fontsize=6.6, color=MUTED)
ax.set_yticks(list(ypos.values()))
ax.set_yticklabels([dict((q, l) for q, l, _ in ROWS)[q] for q in qs], fontsize=7.5)
ax.set_xlabel('difference as % of the control value — bars: smallest difference an n = 2 comparison resolves at 80 % power; '
              'points: differences this project has reported as findings')
ax.set_xscale('symlog', linthresh=10); ax.grid(axis='x', color='#e6e5e0', lw=0.6)
h = [plt.Line2D([], [], marker='o', ls='', mfc='none', mec=ORANGE, mew=1.6, label='reported difference **below** its floor — not resolvable at n = 2'),
     plt.Line2D([], [], marker='o', ls='', color=AQUA, label='reported difference above its floor — survives')]
ax.legend(handles=h, frameon=False, fontsize=7.5, loc='lower right')
fig.suptitle('noise-floor: what this project can resolve at two seeds, and which standing findings clear it',
             fontsize=10, x=0.01, ha='left')
fig.tight_layout(); fig.savefig('figures/nf_resolvable.png', dpi=160); plt.close(fig)
print('figures/nf_cells.png figures/nf_resolvable.png')
