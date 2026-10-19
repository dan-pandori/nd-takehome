#!/usr/bin/env python3
"""figures/ratio.{pdf,png}: RL compute / pretraining compute per model, log axis (run rl-compute-share).

Reads compute_table.csv (build_table.py) and frontier_ranges.csv. Colour = the create-vs-elicit verdict about that
model (validated categorical slots 1-3 + neutral grey for "no test"); marker = the basis of the ratio; the grey
two-tone band = the frontier-lab estimate for H2 2025-2026 (central / full range, weakest source grade D).
"""
import csv, math, os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Patch

HERE = os.path.dirname(os.path.abspath(__file__))
SURF, INK, INK2, MUTED, GRID, BASE = '#fcfcfb', '#0b0b0b', '#52514e', '#898781', '#e1e0d9', '#c3c2b7'
VCOL = {'elicit': '#2a78d6', 'create': '#eb6834', 'mixed': '#1baf7a', 'none': MUTED}
VTXT = {'elicit': 'elicit', 'create': 'create', 'mixed': 'mixed', 'none': 'no test'}
BAND_FULL, BAND_CENTRAL = '#f0efec', '#e1e0d9'
XMIN, XMAX = 1e-6, 1e2

rows = list(csv.DictReader(open(os.path.join(HERE, 'compute_table.csv'))))
front = list(csv.DictReader(open(os.path.join(HERE, 'frontier_ranges.csv'))))
for r in rows:
    r['lo'] = float(r['ratio_low']) if r['ratio_low'] else None
    r['hi'] = float(r['ratio_high']) if r['ratio_high'] else None


def basis(r):
    b = r['ratio_basis']
    if b.startswith('FLOPs from tokens') or b.startswith('FLOPs from our'):
        return 'tok'
    if b.startswith('FLOPs from GPU-hours'):
        return 'hw'
    if 'GPU' in b:
        return 'gpuh'
    if b == 'not computable':
        return 'nc'
    return 'stated'


groups = [
    ('Frontier labs: graded estimates (this review)', None),
    ('Lab disclosures: GPU-hours or stated ratios', [r for r in rows if r['group'] == 'lab']),
    ("Yue et al.'s RL models", [r for r in rows if r['group'] == 'yue']),
    ("Other papers' own RL runs", sorted([r for r in rows if r['group'] == 'lit'],
                                        key=lambda r: -(r['hi'] or r['lo'] or 0))),
    ('Our runs (9.56 M lean_staten, from scratch)', [r for r in rows if r['group'] == 'ours']),
]
items = []   # (kind, payload)
for title, rs in groups:
    items.append(('header', title))
    if rs is None:
        items += [('front', f) for f in front]
    else:
        items += [('row', r) for r in rs]

H = 0.165 * len(items) + 2.4
fig, ax = plt.subplots(figsize=(11.5, H))
fig.patch.set_facecolor(SURF); ax.set_facecolor(SURF)
ax.set_xscale('log'); ax.set_xlim(XMIN, XMAX)
n = len(items)
ax.set_ylim(n - 0.4, -2.6)

# frontier band (H2 2025 - 2026)
b = [f for f in front if f['period'] == 'H2 2025-2026 (band)'][0]
ax.axvspan(float(b['low']), float(b['high']), color=BAND_FULL, zorder=0, lw=0)
ax.axvspan(float(b['central_low']), float(b['central_high']), color=BAND_CENTRAL, zorder=0, lw=0)
ax.text(math.sqrt(float(b['central_low']) * float(b['central_high'])), -2.45,
        'frontier labs H2 2025-26, units as stated\n(mostly GPU-time; FLOPs 2.5-15x lower)\ncentral 0.3-2 (dark), range 0.1-5 (light), grade D',
        ha='center', va='top', fontsize=6.5, color=INK2, zorder=3)
for x in [10.0 ** k for k in range(-6, 3)]:
    ax.axvline(x, color=GRID, lw=0.6, zorder=0.5)
ax.axvline(1.0, color=BASE, lw=1.0, zorder=0.6)

labels = []
for i, (kind, p) in enumerate(items):
    if kind == 'header':
        ax.text(XMIN * 1.15, i, p, fontsize=8, fontweight='bold', color=INK, va='center', zorder=4)
        labels.append('')
        continue
    if kind == 'front':
        if p['period'] == 'H2 2025-2026 (band)':
            labels.append(''); continue
        lo, hi, cl, ch = (float(p[k]) for k in ('low', 'high', 'central_low', 'central_high'))
        ax.plot([lo, hi], [i, i], color=INK2, lw=1.2, solid_capstyle='round', zorder=2)
        ax.plot([cl, ch], [i, i], color=INK2, lw=4.5, solid_capstyle='round', zorder=2)
        ax.text(hi * 1.6, i, f"grade {p['grade']}", fontsize=6.5, color=INK2, va='center')
        labels.append(p['period'])
        continue
    r = p
    col = INK if r['group'] == 'ours' else VCOL.get(r['verdict'], MUTED)
    bs = basis(r)
    lo, hi = r['lo'], r['hi']
    lab = r['model'] if len(r['model']) <= 62 else r['model'][:60] + '…'
    labels.append(lab)
    if bs == 'nc' or lo is None:
        ax.text(XMIN * 1.3, i, 'ratio not computable (size / pretraining / steps undisclosed)', fontsize=6.5,
                color=MUTED, va='center', style='italic')
    else:
        mk = {'tok': 'o', 'hw': 'o', 'gpuh': 's', 'stated': '^'}[bs]
        if r['group'] == 'ours':
            mk = 'D'
        face = 'none' if bs == 'hw' else col
        if hi is None:      # lower bound
            ax.annotate('', xy=(lo * 6, i), xytext=(lo, i),
                        arrowprops=dict(arrowstyle='-|>', color=col, lw=1.4, mutation_scale=8), zorder=3)
            ax.plot([lo], [i], marker=mk, ms=5.5, color=col, mfc=face, mec=col, mew=1.2, zorder=4, ls='none')
            hi_txt = lo * 6
        else:
            if hi > lo * 1.001:
                ax.plot([lo, hi], [i, i], color=col, lw=2.0, solid_capstyle='round', zorder=3,
                        ls=(0, (2, 1.5)) if bs == 'hw' else '-')
            ax.plot([lo, hi] if hi > lo * 1.001 else [lo], [i, i] if hi > lo * 1.001 else [i], marker=mk, ms=5.5,
                    color=col, mfc=face, mec=col, mew=1.2, ls='none', zorder=4)
            hi_txt = hi
        vt = VTXT.get(r['verdict'], '') if r['group'] != 'ours' else ''
        if vt:
            ax.text(min(hi_txt * 1.7, XMAX * 0.5), i, vt, fontsize=6.3, color=INK2, va='center')

ax.set_yticks(range(n)); ax.set_yticklabels(labels, fontsize=6.6, color=INK)
ax.tick_params(axis='y', length=0)
ax.tick_params(axis='x', colors=INK2, labelsize=8)
for s in ('top', 'right', 'left'):
    ax.spines[s].set_visible(False)
ax.spines['bottom'].set_color(BASE)
ax.set_xlabel('RL compute / pretraining compute of the same model (log scale; 1 = equal)', fontsize=8.5, color=INK)
TOP_IN, BOT_IN = 1.05, 0.75
fig.subplots_adjust(left=0.29, right=0.985, top=1 - TOP_IN / H, bottom=BOT_IN / H)
fig.text(0.01, 1 - 0.12 / H, 'How much RL relative to pretraining? Create-vs-elicit papers, lab disclosures, frontier '
         'estimates and our runs', fontsize=10.5, color=INK, va='top', ha='left')
legend = [Line2D([0], [0], color=VCOL['elicit'], lw=2, marker='o', ms=5, label='verdict: elicit / narrows'),
          Line2D([0], [0], color=VCOL['create'], lw=2, marker='o', ms=5, label='verdict: create / expands'),
          Line2D([0], [0], color=VCOL['mixed'], lw=2, marker='o', ms=5, label='verdict: mixed'),
          Line2D([0], [0], color=VCOL['none'], lw=2, marker='o', ms=5, label='no create-vs-elicit test'),
          Line2D([0], [0], color=INK, lw=2, marker='D', ms=5, label='our runs: LLM-equivalent RL-only to as-run'),
          Line2D([0], [0], color=INK2, lw=2, marker='o', ms=5, label='FLOPs from tokens (low to high)'),
          Line2D([0], [0], color=INK2, lw=2, ls=(0, (2, 1.5)), marker='o', mfc='none', ms=5, label='FLOPs from GPU-h x MFU 3-30 %'),
          Line2D([0], [0], color=INK2, lw=0, marker='s', ms=5, label='GPU-hour ratio'),
          Line2D([0], [0], color=INK2, lw=0, marker='^', ms=5, label='stated ratio'),
          Line2D([0], [0], color=INK2, lw=1.2, marker='>', ms=5, label='arrow: lower bound (any marker)'),
          Patch(facecolor=BAND_CENTRAL, edgecolor='none', label='frontier H2 2025-26: central'),
          Patch(facecolor=BAND_FULL, edgecolor='none', label='frontier H2 2025-26: range')]
fig.legend(handles=legend, loc='upper left', bbox_to_anchor=(0.01, 1 - 0.38 / H), ncol=4, fontsize=6.8,
           frameon=False, labelcolor=INK2, handlelength=2.2, columnspacing=1.6)
fig.text(0.01, 0.12 / H, 'Sources, assumptions and every value: rl_compute_share/compute_table.csv (the table view), '
         'ledger/*.tsv, frontier_ranges.csv, our_runs.csv.\nPretraining = 6ND; RL = 2N per generated token + 6N per '
         'trained token (+2N per extra forward pass); N cancels when RL runs on the pretrained model itself.',
         fontsize=6.0, color=MUTED, va='bottom')
os.makedirs(os.path.join(HERE, 'figures'), exist_ok=True)
for ext in ('pdf', 'png'):
    fig.savefig(os.path.join(HERE, 'figures', f'ratio.{ext}'), dpi=170, facecolor=SURF)
print('wrote figures/ratio.{pdf,png}', len(items), 'rows')
