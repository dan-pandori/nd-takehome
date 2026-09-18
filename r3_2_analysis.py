#!/usr/bin/env python3
"""Round 3 run 2 analysis: per-stratum / per-schema / per-round reductio acquisition on the 345 pool, the 8-line ignition
table, six-line coverage, and the cap-8 derived-ORE acquisition vs base reachability (f as marker).
  python r3_2_analysis.py [--out artifacts/r3_2/summary.json] [--figs figures]
Counting rules (preregistration/round3-run2.md): acquisition per stratum from found_<last>.jsonl with the min-round rule
over (theorem, normalised proof) pairs; a target is acquired at round r if some strict-pattern proof of it has min round
<= r; stratum from the pool file; ignition = >= 10 targets of the stratum; violations = targets solved by round r with no
pattern proof (oracle errors). Every number here is reproducible from the pulled files named in the output.
"""
import argparse, json, os, sys, glob, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from normalize import norm
from patterns import classify

IGNITE = 10
POOL6 = 'data/r3_2/targets_reductio_req6.jsonl'
POOL5 = 'data/p2/targets_reductio_req.jsonl'
TRANSFER_R = 'data/p2/transfer_reductio_req.jsonl'
POOL_D = 'data/p2/targets_derived_ore_req.jsonl'
TRANSFER_D = 'data/p2/transfer_derived_ore_req.jsonl'


def rd(fn):
    return [json.loads(l) for l in open(fn) if l.strip()]


def pool_info(fn, stratum_field):
    T = rd(fn)
    return {t['name']: {'stratum': t.get(stratum_field) if stratum_field != 'n_lines' else t['n_lines'], 'schema': t.get('schema')} for t in T}


def arm(d, pattern, info, tinfo):
    """One arm directory -> per-round metrics per stratum. Uses found_<last>.jsonl (cumulative) with the min-round rule."""
    rounds = sorted(int(f.split('_')[-1].split('.')[0]) for f in glob.glob(f'{d}/round_*.json'))
    if not rounds:
        return None
    last = rounds[-1]
    st = {r: json.load(open(f'{d}/round_{r}.json')) for r in rounds}
    k = st[last]['k']
    out = {'dir': d, 'rounds': last, 'k': k, 'attempts': last * k, 'source_files': [f'{d}/found_{last}.jsonl', f'{d}/found_transfer_{last}.jsonl', f'{d}/round_*.json'],
           'secs_per_round': [round(st[r].get('secs', 0)) for r in rounds], 'heldout_greedy': [st[r]['heldout_greedy']['rate'] for r in rounds],
           'solved_per_round': [st[r]['targets_cum']['solved'] for r in rounds]}
    for pool, base, inf in (('targets', 'found', info), ('transfer', 'found_transfer', tinfo)):
        fn = f'{d}/{base}_{last}.jsonl'
        if not os.path.exists(fn):
            continue
        recs = rd(fn)
        minround = {}
        for x in recs:
            key = (x['name'], norm(x['proof'])); minround[key] = min(minround.get(key, 99), x['round'])
        first_pat = {}       # name -> min round of a pattern proof
        first_any = {}       # name -> min round of any proof
        n_pat_proofs = 0; written = collections.Counter()
        for (name, pn), r0 in minround.items():
            first_any[name] = min(first_any.get(name, 99), r0)
            c = classify(pn)
            if c and c[pattern]:
                first_pat[name] = min(first_pat.get(name, 99), r0); n_pat_proofs += 1
                written[c['pruned_len']] += 1
        strata = sorted({v['stratum'] for v in inf.values()}, key=lambda s: (s is None, s))
        per = {}
        for s in strata:
            names = [n for n, v in inf.items() if v['stratum'] == s]
            cum = [sum(1 for n in names if first_pat.get(n, 99) <= r) for r in rounds]
            cum_solved = [sum(1 for n in names if first_any.get(n, 99) <= r) for r in rounds]
            ign = next((r for r, c in zip(rounds, cum) if c >= IGNITE), None)
            fr = min((first_pat[n] for n in names if n in first_pat), default=None)
            per[str(s)] = {'n': len(names), 'cum_acquired': cum, 'cum_solved': cum_solved, 'acquired': cum[-1], 'first_round': fr, 'ignition_round': ign,
                           'by_schema': dict(sorted(collections.Counter(inf[n]['schema'] for n in names if n in first_pat).items()))}
        viol = [n for n in first_any if n not in first_pat]
        out[pool] = {'n': len(inf), 'acquired': len(first_pat), 'solved': len(first_any), 'pattern_proofs': n_pat_proofs, 'violations': len(viol), 'violation_names': viol[:10],
                     'per_stratum': per, 'first_round': min(first_pat.values(), default=None), 'written_pruned_hist': dict(sorted(written.items())),
                     'cum_acquired': [sum(1 for n in first_pat if first_pat[n] <= r) for r in rounds],
                     'by_schema': dict(sorted(collections.Counter(inf[n]['schema'] for n in first_pat).items()))}
    return out


def coverage(fn, pattern):
    if not os.path.exists(fn):
        return None
    rs = rd(fn)
    reach = sorted(r['name'] for r in rs if r['distinct_by_pattern'].get(pattern, 0) > 0)
    return {'file': fn, 'targets': len(rs), 'samples': sum(r['n_tried'] for r in rs), 'solved': sum(r['n_ok'] > 0 for r in rs), 'hits': sum(r['n_ok'] for r in rs),
            'pattern_hits': sum(r['hits_by_pattern'].get(pattern, 0) for r in rs), 'targets_with_pattern_proof': len(reach), 'reachable_names': reach,
            'solved_within_256': sum(r['first_hit'] is not None and r['first_hit'] <= 256 for r in rs),
            'solved_without_pattern': sum(r['n_ok'] > 0 and r['distinct_by_pattern'].get(pattern, 0) == 0 for r in rs),
            'rate_per_sample': sum(r['hits_by_pattern'].get(pattern, 0) for r in rs) / max(1, sum(r['n_tried'] for r in rs)),
            'per_target_hits': sorted((r['hits_by_pattern'].get(pattern, 0) for r in rs), reverse=True)[:12]}


def solved_names(d, pattern):
    """names acquired (strict pattern proof) at the last round of an arm."""
    rounds = sorted(int(f.split('_')[-1].split('.')[0]) for f in glob.glob(f'{d}/round_*.json'))
    fn = f'{d}/found_{rounds[-1]}.jsonl'
    names = set()
    for x in rd(fn):
        c = classify(norm(x['proof']))
        if c and c[pattern]:
            names.add(x['name'])
    return names


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--out', default='artifacts/r3_2/summary.json'); ap.add_argument('--figs', default='figures'); ap.add_argument('--no_figs', action='store_true')
    a = ap.parse_args()
    res = {'reductio': {'pool': POOL6, 'arms': {}, 'run5_arms': {}, 'coverage_six': {}}, 'derived_ore_strict': {'pool': POOL_D, 'label': 'cap 8, not a submission result', 'arms': {}, 'coverage': {}}}
    info6 = pool_info(POOL6, 'stratum'); tinfo = pool_info(TRANSFER_R, 'n_lines')
    res['reductio']['strata'] = dict(sorted(collections.Counter(str(v['stratum']) for v in info6.values()).items()))
    for d in sorted(glob.glob('artifacts/r3_2/*_reductio_*')):
        if os.path.isdir(d):
            m = arm(d, 'reductio', info6, tinfo)
            if m:
                res['reductio']['arms'][os.path.basename(d)] = m
    info5 = pool_info(POOL5, 'n_lines')
    for d in sorted(glob.glob('artifacts/r5/ei_reductio_*_req') + glob.glob('artifacts/r5/frozen_reductio_*_req')):
        m = arm(d, 'reductio', info5, tinfo)
        if m:
            res['reductio']['run5_arms'][os.path.basename(d)] = m
    for s in (0, 1, 2):
        c = coverage(f'artifacts/r3_2/cov6_reductio_f0_s{s}.s0.jsonl', 'reductio')
        if c:
            res['reductio']['coverage_six'][f'f0_s{s}'] = c
    # ignition table for the 8-line stratum (and every stratum), A arms x rounds
    R = res['reductio']
    R['ignition_table'] = {name: {s: m['targets']['per_stratum'][s]['cum_acquired'] for s in m['targets']['per_stratum']} for name, m in R['arms'].items() if 'targets' in m}
    R['ignition_summary'] = {}
    for grp, pre in (('A_ei16', 'ei16_'), ('B_ei8k64', 'ei8k64_'), ('C_ei8', 'ei8_'), ('frozen16', 'frozen16_'), ('frozen8', 'frozen8_')):
        arms = {n: m for n, m in R['arms'].items() if n.startswith(pre) and 'targets' in m}
        R['ignition_summary'][grp] = {'n_arms': len(arms)}
        for s in ('6', '7', '8', '9', '10'):
            R['ignition_summary'][grp][s] = {'ignited_arms': sum(1 for m in arms.values() if m['targets']['per_stratum'].get(s, {}).get('ignition_round') is not None),
                                             'acquired': {n: m['targets']['per_stratum'].get(s, {}).get('acquired') for n, m in arms.items()},
                                             'first_round': {n: m['targets']['per_stratum'].get(s, {}).get('first_round') for n, m in arms.items()},
                                             'ignition_round': {n: m['targets']['per_stratum'].get(s, {}).get('ignition_round') for n, m in arms.items()}}
    # derived-ORE, cap 8
    infoD = pool_info(POOL_D, 'n_lines'); tinfoD = pool_info(TRANSFER_D, 'n_lines')
    D = res['derived_ore_strict']
    for d in sorted(glob.glob('artifacts/r3_2/*_dore_*')):
        if os.path.isdir(d):
            m = arm(d, 'derived_ore_strict', infoD, tinfoD)
            if m:
                D['arms'][os.path.basename(d)] = m
    for d in sorted(glob.glob('artifacts/r5/ei_derived_ore_strict_*_req') + glob.glob('artifacts/r5/frozen_derived_ore_strict_*_req')):
        m = arm(d, 'derived_ore_strict', infoD, tinfoD)
        if m:
            D['arms']['r5/' + os.path.basename(d)] = m
    covs = {'f0_c8_s0': 'artifacts/r5/cov_derived_ore_strict_f0_c8_s0_req.s0.jsonl', 'f0_c8_s1': 'artifacts/r5/cov_derived_ore_strict_f0_c8_s1_req.s0.jsonl',
            'f0_c8_s2': 'artifacts/r3_2/cov_dore_f0_c8_s2.s0.jsonl', 'f0_c8_s3': 'artifacts/r3_2/cov_dore_f0_c8_s3.s0.jsonl'}
    for tag, fn in covs.items():
        c = coverage(fn, 'derived_ore_strict')
        if c:
            D['coverage'][tag] = c
    # EI acquisition vs base reachability for the f = 0 draws (EI-only = acquired but not base-reachable at 1e4)
    D['f0_draws'] = {}
    pairs = {'f0_c8_s0': ('artifacts/r5/ei_derived_ore_strict_f0_c8_s0_req', 'artifacts/r5/frozen_derived_ore_strict_f0_c8_s0_req'),
             'f0_c8_s1': ('artifacts/r5/ei_derived_ore_strict_f0_c8_s1_req', 'artifacts/r5/frozen_derived_ore_strict_f0_c8_s1_req'),
             'f0_c8_s2': ('artifacts/r3_2/ei_dore_f0_c8_s2', 'artifacts/r3_2/frozen_dore_f0_c8_s2'), 'f0_c8_s3': ('artifacts/r3_2/ei_dore_f0_c8_s3', 'artifacts/r3_2/frozen_dore_f0_c8_s3')}
    for tag, (ei, fr) in pairs.items():
        if tag in D['coverage'] and glob.glob(f'{ei}/round_*.json'):
            reach = set(D['coverage'][tag]['reachable_names']); got = solved_names(ei, 'derived_ore_strict')
            frn = solved_names(fr, 'derived_ore_strict') if glob.glob(f'{fr}/round_*.json') else set()
            r = len(reach)
            D['f0_draws'][tag] = {'base_reachable': r, 'ei_acquired': len(got), 'ei_acq': len(got) / 300, 'ei_base_reachable': len(got & reach), 'ei_only': len(got - reach),
                                  'frozen_acquired': len(frn), 'ei_over_base': len(got) / r if r else None, 'ei_over_frozen': len(got) / len(frn) if frn else None,
                                  'base_rate_per_sample': D['coverage'][tag]['rate_per_sample'], 'source': [ei, fr, D['coverage'][tag]['file']]}
    D['f_dial'] = {}
    for f, names in ((0, ['r5/ei_derived_ore_strict_f0_c8_s0_req', 'r5/ei_derived_ore_strict_f0_c8_s1_req', 'ei_dore_f0_c8_s2', 'ei_dore_f0_c8_s3']),
                     (0.001, ['ei_dore_f0.001_c8_s0', 'ei_dore_f0.001_c8_s1']), (0.01, ['r5/ei_derived_ore_strict_f0.01_c8_s0_req', 'r5/ei_derived_ore_strict_f0.01_c8_s1_req'])):
        vals = {n: D['arms'][n]['targets']['acquired'] / 300 for n in names if n in D['arms']}
        frs = {n: D['arms'][n.replace('ei_', 'frozen_').replace('r5/ei_', 'r5/frozen_')]['targets']['acquired'] / 300 for n in names if n.replace('ei_', 'frozen_').replace('r5/ei_', 'r5/frozen_') in D['arms']}
        D['f_dial'][str(f)] = {'ei': vals, 'frozen': frs, 'ei_mean': sum(vals.values()) / len(vals) if vals else None}
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    json.dump(res, open(a.out, 'w'), indent=1)
    # ---- print
    print(f"== reductio pool {POOL6}: strata {R['strata']}")
    for name, m in list(R['arms'].items()) + [('r5/' + n, m) for n, m in R['run5_arms'].items()]:
        if 'targets' not in m:
            continue
        t = m['targets']; ps = t['per_stratum']
        print(f"  {name:34s} r{m['rounds']:2d} k{m['k']:2d} acq {t['acquired']:3d}/{t['n']} viol {t['violations']} | " + ' '.join(f"{s}:{ps[s]['acquired']:3d}/{ps[s]['n']:3d}(fr {str(ps[s]['first_round']):>4s} ign {str(ps[s]['ignition_round']):>4s})" for s in ps) + f" | transfer {m.get('transfer', {}).get('acquired')}/{m.get('transfer', {}).get('n')} heldout {m['heldout_greedy'][-1]:.3f} secs/round {sum(m['secs_per_round']) / len(m['secs_per_round']):.0f}")
    for grp, v in R['ignition_summary'].items():
        print(f"  ignition {grp}: " + ' '.join(f"{s}-line {v[s]['ignited_arms']}/{v['n_arms']}" for s in ('6', '7', '8', '9', '10')))
    for tag, c in R['coverage_six'].items():
        print(f"  cov6 {tag}: targets {c['targets']} samples {c['samples']} pattern targets {c['targets_with_pattern_proof']} hits {c['pattern_hits']} rate {c['rate_per_sample']:.2e} solved-without {c['solved_without_pattern']}")
    print(f"== derived-ORE cap 8 ({D['label']})")
    for name, m in D['arms'].items():
        if 'targets' in m:
            print(f"  {name:44s} r{m['rounds']} acq {m['targets']['acquired']:3d}/300 ({m['targets']['acquired'] / 300:.3f}) viol {m['targets']['violations']} per-round {m['targets']['cum_acquired']} transfer {m.get('transfer', {}).get('acquired')}/65")
    for tag, c in D['coverage'].items():
        print(f"  cov {tag}: base-reachable {c['targets_with_pattern_proof']}/300 hits {c['pattern_hits']} rate {c['rate_per_sample']:.2e} within256 {c['solved_within_256']} solved-without {c['solved_without_pattern']}")
    for tag, v in D['f0_draws'].items():
        print(f"  f0 draw {tag}: base {v['base_reachable']} EI {v['ei_acquired']} (= {v['ei_base_reachable']} base-reachable + {v['ei_only']} EI-only) frozen {v['frozen_acquired']} EI/base {v['ei_over_base']} EI/frozen {v['ei_over_frozen']}")
    for f, v in D['f_dial'].items():
        print(f"  f = {f}: EI {v['ei']} frozen {v['frozen']}")
    print('wrote', a.out)
    if a.no_figs:
        return
    import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
    os.makedirs(a.figs, exist_ok=True)
    COL = {'6': '#8c8a85', '7': '#2a78d6', '8': '#eb6834', '9': '#4fa36b', '10': '#9b59b6'}
    A = [n for n in R['arms'] if n.startswith('ei16_') and 'targets' in R['arms'][n]]
    if A:
        fig, axes = plt.subplots(2, 3, figsize=(11, 6), sharex=True, sharey=True)
        for ax, n in zip(axes.flat, sorted(A)):
            m = R['arms'][n]; ps = m['targets']['per_stratum']; x = list(range(1, m['rounds'] + 1))
            for s in ps:
                ax.plot(x, [c / ps[s]['n'] for c in ps[s]['cum_acquired']], color=COL.get(s, '#333'), lw=2, marker='o', ms=2.5, label=f"{s}-line ({ps[s]['n']})")
            fr = n.replace('ei16_', 'frozen16_')
            if fr in R['arms'] and 'targets' in R['arms'][fr]:
                pf = R['arms'][fr]['targets']['per_stratum']
                for s in pf:
                    ax.plot(list(range(1, R['arms'][fr]['rounds'] + 1)), [c / pf[s]['n'] for c in pf[s]['cum_acquired']], color=COL.get(s, '#333'), lw=1, ls='--', alpha=0.7)
            ax.set_title(n.replace('ei16_reductio_', '').replace('_ss', ' · sampling seed '), fontsize=9)
            ax.spines[['top', 'right']].set_visible(False); ax.grid(color='#e8e7e3', lw=0.6); ax.set_axisbelow(True)
        for ax in axes[1]:
            ax.set_xlabel('expert-iteration round (k = 32)')
        for ax in axes[:, 0]:
            ax.set_ylabel('fraction of stratum acquired')
        axes[0, 0].legend(fontsize=7, frameon=False, title='stratum (solid EI, dashed frozen)', title_fontsize=7)
        fig.suptitle('Reductio required pool (345): cumulative acquisition per length stratum, 16 rounds', fontsize=10)
        fig.tight_layout(); fig.savefig(f'{a.figs}/r3_2_strata.png', dpi=160)
    # derived-ORE: EI acquisition vs base reachability, f as marker
    if D['f0_draws'] or D['f_dial']:
        fig, ax = plt.subplots(figsize=(5.2, 4))
        MK = {'0': 'o', '0.001': 's', '0.01': '^'}
        for tag, v in D['f0_draws'].items():
            ax.scatter([v['base_reachable'] / 300], [v['ei_acq']], marker='o', s=70, color='#2a78d6', zorder=4)
            ax.scatter([v['base_reachable'] / 300], [v['frozen_acquired'] / 300], marker='o', s=50, facecolors='none', edgecolors='#2a78d6', zorder=4)
            ax.annotate(tag.replace('f0_c8_', 's'), (v['base_reachable'] / 300, v['ei_acq']), textcoords='offset points', xytext=(5, 3), fontsize=7)
        xs = [0, 0.3]; ax.plot(xs, xs, color='#b4b2ad', lw=1, ls=':'); ax.plot(xs, [2 * x for x in xs], color='#d9d7d2', lw=1, ls=':'); ax.plot(xs, [0.5 * x for x in xs], color='#d9d7d2', lw=1, ls=':')
        ax.set_xlabel('base strict reachability at pass@10⁴ (fraction of 300)'); ax.set_ylabel('EI acquisition after 8 rounds (fraction of 300)')
        ax.set_title('strict derived ORE, cap 8 (not a submission result): f = 0 draws', fontsize=9)
        ax.spines[['top', 'right']].set_visible(False); ax.grid(color='#e8e7e3', lw=0.6); ax.set_axisbelow(True)
        ax.set_xlim(0, max(0.15, max([v['base_reachable'] / 300 for v in D['f0_draws'].values()] + [0.1]) * 1.3)); ax.set_ylim(0, None)
        fig.tight_layout(); fig.savefig(f'{a.figs}/r3_2_dore_base.png', dpi=160)
        fig, ax = plt.subplots(figsize=(5.2, 3.6))
        for f, v in D['f_dial'].items():
            px = 1e-4 if f == '0' else float(f)
            for n, val in v['ei'].items():
                ax.scatter([px], [val], marker=MK[f], s=60, color='#2a78d6', zorder=4)
            for n, val in v['frozen'].items():
                ax.scatter([px], [val], marker=MK[f], s=45, facecolors='none', edgecolors='#2a78d6', zorder=3)
        fs = [k for k, v in D['f_dial'].items() if v['ei_mean'] is not None]
        ax.plot([1e-4 if f == '0' else float(f) for f in fs], [D['f_dial'][f]['ei_mean'] for f in fs], color='#2a78d6', lw=1.5)
        ax.set_xscale('log'); ax.set_xticks([1e-4, 1e-3, 1e-2]); ax.set_xticklabels(['0', '1e-3', '1e-2']); ax.set_xlabel('strict derived-ORE frequency f in pretraining'); ax.set_ylabel('acquisition (fraction of 300)')
        ax.set_title('cap 8 derived ORE: EI (filled) and frozen (open) vs f', fontsize=9); ax.spines[['top', 'right']].set_visible(False); ax.grid(color='#e8e7e3', lw=0.6); ax.set_axisbelow(True); ax.set_ylim(0, None)
        fig.tight_layout(); fig.savefig(f'{a.figs}/r3_2_dore_fdial.png', dpi=160)
    print('figures written to', a.figs)


if __name__ == '__main__':
    main()
