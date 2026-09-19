#!/usr/bin/env python3
"""round3-run4b figures from artifacts/r3_4b/summary.json and artifacts/r3_4b/diag_*.json.

  python3 r3_4b_figures.py -> figures/r3_4b_fractions.png  (non-zero fraction and EI-only fraction vs parameters)
                              figures/r3_4b_mix_curves.png (mix-arm acquisition per round, one panel per size / schedule)
                              figures/r3_4b_writing.png    (share of base samples that open a third box, per draw, vs mix ignition)
Colours: the dataviz default categorical slots in fixed order (blue, orange, aqua); text in ink colours, recessive grid.
"""
import json, glob, os, re
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

S = json.load(open('artifacts/r3_4b/summary.json'))
BLUE, ORANGE, AQUA, INK, INK2, GRID, SURF = '#2a78d6', '#eb6834', '#1baf7a', '#0b0b0b', '#52514e', '#e4e3df', '#fcfcfb'
GROUPS = [('3.2M', '3.2M\n(run 1)', 3.2e6), ('25M', '25M\nfirst schedule\n(gate missed)', 25.3e6), ('25Mr', '25M\nretry\n(gate passed)', 25.3e6),
          ('85M', '85M\nfirst schedule\n(gate missed)', 85.2e6), ('85Mr', '85M\nretry\n(gate missed)', 85.2e6)]
plt.rcParams.update({'font.size': 9, 'axes.edgecolor': GRID, 'axes.labelcolor': INK2, 'xtick.color': INK2, 'ytick.color': INK2,
                     'axes.facecolor': SURF, 'figure.facecolor': SURF, 'savefig.facecolor': SURF, 'axes.spines.top': False, 'axes.spines.right': False})


def draws(size):
    return [d for d in S['sizes'].get(size, {}).values() if d.get('pre_rl')]


def frac_fig():
    fig, ax = plt.subplots(1, 3, figsize=(12.5, 3.8), sharey=True)
    present = [(k, lab) for k, lab, _ in GROUPS if draws(k)]
    xs = range(len(present))
    panels = [('non-zero draws, required pool\n(>= 1 pattern hit in 600k pre-RL samples)', lambda d: d['pre_rl'] and not d['pre_rl']['zero_rate'], lambda d: bool(d.get('pre_rl')), BLUE),
              ('draws whose mix arm ignites\n(>= 20 required targets by round 8)', lambda d: d['mix']['ignition_round'] is not None, lambda d: bool(d.get('mix')) and d['mix']['rounds_done'] == 8, ORANGE)]
    for a, (title, hit, ok, col) in zip(ax[:2], panels):
        for x, (k, lab) in zip(xs, present):
            ds = [d for d in draws(k) if ok(d)]
            if not ds:
                continue
            n = sum(bool(hit(d)) for d in ds)
            a.bar(x, n / len(ds), width=0.55, color=col, zorder=3)
            a.text(x, n / len(ds) + 0.03, f'{n} / {len(ds)}', ha='center', color=INK, fontsize=9)
        a.set_title(title, fontsize=9, color=INK, loc='left'); a.set_xticks(list(xs)); a.set_xticklabels([lab for _, lab in present], fontsize=7.5)
        a.set_ylim(0, 1.15); a.grid(axis='y', color=GRID, zorder=0); a.set_axisbelow(True)
    ax[0].set_ylabel('fraction of Stage-1 draws')
    a = ax[2]
    for x, (k, lab) in zip(xs, present):
        es = [(d.get('ei_only_mix') or d.get('ei_only_mix_at_2000'), bool(d.get('ei_only_mix'))) for d in draws(k)]
        es = [(e, full) for e, full in es if e and e['acquired'] >= 20]
        for j, (e, full) in enumerate(es):
            if True:
                a.plot([x + (j - (len(es) - 1) / 2) * 0.13], [e['fraction']], 'o', ms=8, mfc=AQUA if full else SURF, mec=AQUA, mew=2, zorder=3)
    a.plot([], [], 'o', ms=8, mfc=AQUA, mec=AQUA, label='base sampled at 10^4 per target')
    a.plot([], [], 'o', ms=8, mfc=SURF, mec=AQUA, mew=2, label='base sampled at 2,000 per target only')
    a.legend(frameon=False, fontsize=7.5, loc='lower left', labelcolor=INK2)
    a.set_title('EI-only fraction, igniting mix arms\n(acquired targets the base never reaches / acquired)', fontsize=9, color=INK, loc='left')
    a.set_xticks(list(xs)); a.set_xticklabels([lab for _, lab in present], fontsize=7.5); a.grid(axis='y', color=GRID, zorder=0)
    fig.tight_layout(); fig.savefig('figures/r3_4b_fractions.png', dpi=160); plt.close(fig)


def curves_fig():
    present = [(k, lab) for k, lab, _ in GROUPS if any(d.get('mix') for d in S['sizes'].get(k, {}).values())]
    fig, ax = plt.subplots(1, len(present), figsize=(2.6 * len(present), 3.2), sharey=True)
    for a, (k, lab) in zip(ax, present):
        for d in S['sizes'][k].values():
            m = d.get('mix')
            if not m:
                continue
            y = [p['pattern_required'] for p in m['per_round']]
            ign = m['ignition_round'] is not None
            a.plot(range(1, len(y) + 1), y, '-', lw=2, color=ORANGE if ign else INK2, alpha=1 if ign else 0.55, zorder=3)
        a.set_title(lab.replace('\n', ' '), fontsize=8, color=INK, loc='left'); a.set_xlabel('round'); a.set_xticks([2, 4, 6, 8]); a.grid(color=GRID, zorder=0); a.set_ylim(-5, 300)
    ax[0].set_ylabel('required targets with a depth-3 proof\n(mix arm, cumulative, of 300)')
    ax[-1].plot([], [], '-', lw=2, color=ORANGE, label='ignites'); ax[-1].plot([], [], '-', lw=2, color=INK2, alpha=0.55, label='does not'); ax[-1].legend(frameon=False, fontsize=8, labelcolor=INK2)
    fig.tight_layout(); fig.savefig('figures/r3_4b_mix_curves.png', dpi=160); plt.close(fig)


def writing_fig():
    fig, a = plt.subplots(figsize=(6.4, 3.4))
    present = [(k, lab) for k, lab, _ in GROUPS if glob.glob(f'artifacts/r3_4b/diag_{k}_s*.json')]
    for x, (k, lab) in enumerate(present):
        fns = sorted(glob.glob(f'artifacts/r3_4b/diag_{k}_s*.json'))
        for j, fn in enumerate(fns):
            D = json.load(open(fn)); s = re.search(r'_s(\d+)\.json', fn).group(1)
            m = (S['sizes'].get(k, {}).get(f's{s}') or {}).get('mix')
            ign = bool(m and m['ignition_round'] is not None); known = bool(m and m['rounds_done'] == 8)
            a.plot([x + (j - (len(fns) - 1) / 2) * 0.09], [max(D['frac_depth_ge3'], 1e-4)], 'o', ms=8, mfc=ORANGE if ign else SURF, mec=ORANGE if ign else INK2, mew=2, alpha=1 if known else 0.4, zorder=3)
    a.set_yscale('log'); a.set_ylim(7e-5, 0.2); a.set_xticks(range(len(present))); a.set_xticklabels([lab for _, lab in present], fontsize=7.5)
    a.set_ylabel('share of base samples that open a third box\n(3,840 samples; 0 plotted at 1e-4)'); a.grid(axis='y', color=GRID, zorder=0)
    a.plot([], [], 'o', ms=8, mfc=ORANGE, mec=ORANGE, label='mix arm ignites'); a.plot([], [], 'o', ms=8, mfc=SURF, mec=INK2, mew=2, label='does not (faded: arm not finished)')
    a.legend(frameon=False, fontsize=8, labelcolor=INK2, loc='lower left')
    a.set_title('What the base writes before RL: none of these samples verifies', fontsize=9, color=INK, loc='left')
    fig.tight_layout(); fig.savefig('figures/r3_4b_writing.png', dpi=160); plt.close(fig)


if __name__ == '__main__':
    os.makedirs('figures', exist_ok=True)
    frac_fig(); curves_fig(); writing_fig()
    print('figures written')
