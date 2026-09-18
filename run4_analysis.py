#!/usr/bin/env python3
"""Run 4 (GRPO vs EI at f = 0) — summary numbers and figures from the pulled artefacts.

  python3 run4_analysis.py --out artifacts/r4/summary.json --figdir figures

Reads artifacts/r4/{grpo_*,ei_*,frozen_*}/round_<r>.json + found_<r>.jsonl (metrics via phase2_metrics.arm_metrics:
depth-3 acquisition on the model's pruned, start-index-normalised proof, min-round rule), artifacts/r4/grpo_*/updates.jsonl
(per-update trace) and artifacts/r4/cov_depth3_f0_a1_s<s>.s0.jsonl (base rate: depth-3 hits / samples on the first 300 targets).
Ignition = first round with >= 20 depth-3 target theorems (2 % of 1,000), as in the ignition study.
"""
import argparse, json, os, sys, glob, re, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from phase2_metrics import arm_metrics

IGN = 20


def parse_arm(name):
    # grpo_g8_depth3_f0_a1_s20[_lr3e-5][_e2] | grpo_sprint_depth3_f0_a1_s20_lr1e-5 | ei_depth3_f0_a1_s20[_e2] | frozen_depth3_f0_a1_s20
    m = re.match(r'(grpo_g(\d+)|grpo_sprint|ei|frozen)_depth3_f0_a1_s(\d+)(_lr[0-9e.-]+)?(_e2)?$', name)
    if not m:
        return None
    kind = m.group(1)
    G = int(m.group(2)) if m.group(2) else None
    lr = m.group(4)[3:] if m.group(4) else ('1e-4' if kind.startswith('grpo') else None)
    return {'arm': name, 'kind': 'grpo' if kind.startswith('grpo_g') else kind, 'G': G, 'draw': int(m.group(3)), 'lr': lr, 'seed2': bool(m.group(5))}


def coverage(draw):
    fn = f'artifacts/r4/cov_depth3_f0_a1_s{draw}.s0.jsonl'
    if not os.path.exists(fn):
        return None
    recs = [json.loads(l) for l in open(fn) if l.strip()]
    hits = sum(r['hits_by_pattern'].get('depth3', 0) for r in recs)
    tried = sum(r['n_tried'] for r in recs)
    thms = sum(1 for r in recs if r['hits_by_pattern'].get('depth3', 0) > 0)
    ok = sum(r['n_ok'] for r in recs)
    solved = sum(1 for r in recs if r['n_ok'] > 0)
    # frozen control at 256 attempts on these targets: first depth-3 sample index <= 256
    f256 = sum(1 for r in recs if any(p['pat'].get('depth3') and p['first'] <= 256 for p in r['proofs']))
    return {'n_targets': len(recs), 'samples': tried, 'depth3_hits': hits, 'depth3_targets': thms, 'rate': hits / tried if tried else None,
            'verified_samples': ok, 'targets_solved': solved, 'depth3_targets_within_256': f256}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', default='artifacts/r4/summary.json')
    ap.add_argument('--figdir', default='figures')
    ap.add_argument('--no_fig', action='store_true')
    a = ap.parse_args()
    arms = {}
    for d in sorted(glob.glob('artifacts/r4/*/')):
        name = os.path.basename(d.rstrip('/'))
        p = parse_arm(name)
        if not p or not glob.glob(f'{d}/round_*.json'):
            continue
        m = arm_metrics(d.rstrip('/'), 'depth3')
        curve = [x['acq_targets_theorems'] for x in m]
        ign = next((x['round'] for x in m if x['acq_targets_theorems'] >= IGN), None)
        last = m[-1]
        p.update({'rounds': len(m), 'depth3_theorems_by_round': curve, 'ignition_round': ign,
                  'acq': last['acq_targets'], 'acq_theorems': last['acq_targets_theorems'], 'n_depth3_proofs': last['n_pattern_proofs_targets'],
                  'first_round': last['first_round_pattern_targets'], 'targets_solved': last['targets_solved'],
                  'solved_by_round': [x['targets_solved'] for x in m],
                  'transfer_acq': last['acq_transfer'], 'transfer_solved': last['transfer_solved'],
                  'heldout_greedy_by_round': [x['heldout_greedy'] for x in m], 'transfer_greedy_by_round': [x['transfer_greedy'] for x in m],
                  'distinct_proofs': last['distinct_proofs_targets']})
        ufn = f'{d}/updates.jsonl'
        if os.path.exists(ufn):
            ups = [json.loads(l) for l in open(ufn) if l.strip()]
            p['updates'] = len(ups)
            p['var_frac_by_update'] = [u['var_frac'] for u in ups]
            p['cum_pattern_targets_by_update'] = [u['cum_pattern_targets'] for u in ups]
            p['cum_solved_by_update'] = [u['cum_solved_targets'] for u in ups]
            p['sample_acc_by_update'] = [u['sample_acc'] for u in ups]
            p['first_pattern_update'] = next((u['update'] for u in ups if u['pattern_samples'] > 0), None)
            p['ignition_update'] = next((u['update'] for u in ups if u['cum_pattern_targets'] >= IGN), None)
            p['samples_per_update'] = ups[0]['groups'] * ups[0]['group_size']
            p['var_frac_update1'] = ups[0]['var_frac']
            p['var_frac_round1'] = sum(u['var_frac'] for u in ups[:40]) / min(40, len(ups))
            p['var_frac_last40'] = sum(u['var_frac'] for u in ups[-40:]) / min(40, len(ups))
            p['secs_total'] = sum(u['secs'] for u in ups)
        arms[name] = p
    draws = sorted({p['draw'] for p in arms.values()})
    cov = {s: coverage(s) for s in draws}
    summary = {'ignition_threshold': IGN, 'arms': arms, 'coverage': cov}
    # console table
    print(f"{'arm':44s} {'draw':4s} {'kind':6s} {'G':>3s} {'lr':>5s} {'rnds':>4s} {'ign':>4s} {'acq':>6s} {'thms':>5s} {'solved':>6s} {'xfer':>6s} {'H8':>6s} {'var1':>6s} {'varL':>6s} {'1stpat':>6s} {'ignU':>5s}")
    for name, p in sorted(arms.items(), key=lambda x: (x[1]['draw'], x[1]['kind'], x[1]['G'] or 0, x[1]['lr'] or '', x[1]['seed2'])):
        print(f"{name:44s} {p['draw']:<4d} {p['kind']:6s} {str(p['G'] or '-'):>3s} {str(p['lr'] or '-'):>5s} {p['rounds']:4d} {str(p['ignition_round']):>4s} {p['acq']:6.3f} {p['acq_theorems']:5d} {p['targets_solved']:6d} {p['transfer_acq']:6.3f} {p['heldout_greedy_by_round'][-1]:6.3f} "
              f"{p.get('var_frac_update1', float('nan')):6.3f} {p.get('var_frac_last40', float('nan')):6.3f} {str(p.get('first_pattern_update', '-')):>6s} {str(p.get('ignition_update', '-')):>5s}")
    for s in draws:
        c = cov[s]
        print(f"draw s{s}: coverage " + (f"depth-3 hits {c['depth3_hits']} / {c['samples']} (rate {c['rate']:.2e}, {c['depth3_targets']} targets), solved {c['targets_solved']}/{c['n_targets']}, depth-3 targets within 256: {c['depth3_targets_within_256']}" if c else 'missing'))
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    json.dump(summary, open(a.out, 'w'), indent=1)
    if a.no_fig:
        return
    import matplotlib; matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    os.makedirs(a.figdir, exist_ok=True)
    cols = {'ei': '#4c4c4c', 'frozen': '#b0b0b0', ('grpo', 8, '1e-4'): '#c0392b', ('grpo', 32, '1e-4'): '#e67e22', ('grpo', 8, '3e-5'): '#2980b9', ('grpo', 32, '3e-5'): '#16a085'}
    # Fig 1: depth-3 theorems vs samples per draw (GRPO per update, EI per round)
    n = len(draws)
    fig, axes = plt.subplots(2, (n + 1) // 2, figsize=(4.2 * ((n + 1) // 2), 6.4), sharex=True, sharey=True)
    axes = axes.flatten()
    for ax, s in zip(axes, draws):
        for name, p in arms.items():
            if p['draw'] != s or p['kind'] == 'grpo_sprint':
                continue
            if p['kind'] == 'grpo' and p['lr'] in ('1e-4', '3e-5'):
                key = ('grpo', p['G'], p['lr']); xs = [(i + 1) * p['samples_per_update'] / 1000 for i in range(p['updates'])]
                ax.plot(xs, p['cum_pattern_targets_by_update'], color=cols[key], lw=1.2 if not p['seed2'] else 0.8, alpha=1 if not p['seed2'] else 0.6,
                        label=f"GRPO G={p['G']} lr {p['lr']}" if not p['seed2'] else None)
            elif p['kind'] in ('ei', 'frozen'):
                xs = [r * 32 for r in range(1, p['rounds'] + 1)]
                ax.plot(xs, p['depth3_theorems_by_round'], color=cols[p['kind']], marker='o', ms=3, lw=1.2 if not p['seed2'] else 0.8, ls='-' if p['kind'] == 'ei' else '--',
                        label=p['kind'].upper() if not p['seed2'] else None)
        c = cov[s]
        ax.set_title(f"draw s{s}" + (f"  base depth-3 rate {c['rate']:.1e}" if c and c['rate'] else ("  base rate 0 (0/600k)" if c else '')), fontsize=9)
        ax.axhline(IGN, color='k', lw=0.5, ls=':')
        ax.set_xlim(0, 260)
    for ax in axes[-((n + 1) // 2):]:
        ax.set_xlabel('samples per target (thousands of samples / 1,000 targets)', fontsize=8)
    axes[0].set_ylabel('targets solved with a depth-3 proof (cumulative)', fontsize=8)
    axes[0].legend(fontsize=7, loc='lower right')
    fig.suptitle('Run 4: depth-3 acquisition vs sample budget, GRPO (per update) and EI (per round), same Stage-1 draw', fontsize=10)
    fig.tight_layout(); fig.savefig(f'{a.figdir}/run4_acquisition.png', dpi=130); plt.close(fig)
    # Fig 2: fraction of groups with reward variance per update
    fig, axes = plt.subplots(2, (n + 1) // 2, figsize=(4.2 * ((n + 1) // 2), 6.0), sharex=True, sharey=True)
    axes = axes.flatten()
    for ax, s in zip(axes, draws):
        for name, p in arms.items():
            if p['draw'] != s or p['kind'] != 'grpo' or p['seed2'] or p['lr'] not in ('1e-4', '3e-5'):
                continue
            key = ('grpo', p['G'], p['lr'])
            ax.plot(range(1, p['updates'] + 1), p['var_frac_by_update'], color=cols[key], lw=0.9, label=f"G={p['G']} lr {p['lr']}")
        ax.set_title(f'draw s{s}', fontsize=9)
    for ax in axes[-((n + 1) // 2):]:
        ax.set_xlabel('update', fontsize=8)
    axes[0].set_ylabel('fraction of groups with reward variance', fontsize=8); axes[0].legend(fontsize=7)
    fig.tight_layout(); fig.savefig(f'{a.figdir}/run4_variance.png', dpi=130); plt.close(fig)
    # Fig 3: held-out greedy by round
    fig, ax = plt.subplots(figsize=(6, 3.6))
    for name, p in arms.items():
        if p['kind'] == 'grpo_sprint' or p['kind'] == 'frozen':
            continue
        key = ('grpo', p['G'], p['lr']) if p['kind'] == 'grpo' else p['kind']
        if key not in cols:
            continue
        ax.plot(range(1, p['rounds'] + 1), p['heldout_greedy_by_round'], color=cols[key], lw=0.8, alpha=0.7)
    for key, c in cols.items():
        if key != 'frozen':
            ax.plot([], [], color=c, label=(f'GRPO G={key[1]} lr {key[2]}' if isinstance(key, tuple) else key.upper()))
    ax.set_xlabel('round (32 samples per target each)'); ax.set_ylabel('held-out greedy pass@1 (5,000)'); ax.legend(fontsize=7)
    ax.set_title('Run 4: in-distribution accuracy during RL (all draws, both seeds)', fontsize=9)
    fig.tight_layout(); fig.savefig(f'{a.figdir}/run4_heldout.png', dpi=130); plt.close(fig)
    print('figures written to', a.figdir)


if __name__ == '__main__':
    main()
