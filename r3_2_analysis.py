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


def md_bullets(res):
    """numbers.md-ready bullets (every number from the files named in each line)."""
    L = []
    R = res['reductio']
    L.append(f"- Reductio pool `{R['pool']}` (345; strata 6 / 7 / 8 / 9 / 10 = " + ' / '.join(str(R['strata'][s]) for s in ('6', '7', '8', '9', '10')) + "; `data/r3_2/pool_report.json`); transfer `data/p2/transfer_reductio_req.jsonl` (150). Acquisition = targets with a normalised proof containing `patterns.reductio`, min-round rule; ignition = ≥ 10 targets of a stratum; violations = solved without the pattern.")
    for grp, pre, lab in (('A', 'ei16_', 'arm A, 16 rounds × k = 32'), ('B', 'ei8k64_', 'arm B, 8 rounds × k = 64'), ('C', 'ei8_', 'arm C, zero-rate draws, 16 rounds × k = 32 (rounds 9–16 resumed from the round-8 checkpoint)'), ('F16', 'frozen16_', 'frozen controls, 16 × 32 attempts, no training'), ('F8', 'frozen8_', 'frozen controls, 8 × 32')):
        arms = {n: m for n, m in R['arms'].items() if n.startswith(pre) and 'targets' in m}
        if not arms:
            continue
        L.append(f"- {lab} (`artifacts/r3_2/<arm>/found_<last>.jsonl`, `round_*.json`):")
        for n, m in sorted(arms.items()):
            t = m['targets']; ps = t['per_stratum']
            L.append(f"  - `{n}`: rounds {m['rounds']}, attempts {m['attempts']}; acquired **{t['acquired']} / {t['n']}** (per stratum 6 / 7 / 8 / 9 / 10: " + ' / '.join(str(ps[s]['acquired']) for s in ('6', '7', '8', '9', '10')) + "; first-proof round " + ' / '.join(str(ps[s]['first_round']) for s in ('6', '7', '8', '9', '10')) + "; ignition round " + ' / '.join(str(ps[s]['ignition_round']) for s in ('6', '7', '8', '9', '10')) + f"); violations {t['violations']}; transfer {m['transfer']['acquired']} / {m['transfer']['n']} (per stratum 7 / 8 / 9 / 10: " + ' / '.join(str(m['transfer']['per_stratum'][s]['acquired']) for s in ('7', '8', '9', '10')) + f"); heldout greedy {m['heldout_greedy'][-1]:.3f}; 8-line cumulative per round {ps['8']['cum_acquired']}")
    for grp, v in R['ignition_summary'].items():
        if v['n_arms']:
            L.append(f"- Ignition {grp} ({v['n_arms']} arms): 6 / 7 / 8 / 9 / 10-line strata ignited in " + ' / '.join(str(v[s]['ignited_arms']) for s in ('6', '7', '8', '9', '10')) + " arms.")
    for tag, c in R['coverage_six'].items():
        L.append(f"- Six-line base rate {tag} (`{c['file']}`): {c['targets']} targets × 10⁴ = {c['samples']:,} samples; targets with a strict reductio proof **{c['targets_with_pattern_proof']} / 45**, hits {c['pattern_hits']:,} ({c['rate_per_sample']:.2e} per sample), solved within 256 {c['solved_within_256']}, solved without the pattern {c['solved_without_pattern']}.")
    D = res['derived_ore_strict']
    L.append(f"- Derived-ORE (**{D['label']}**) pool `{D['pool']}` (300), transfer (65); acquisition = targets with a `patterns.derived_ore_strict` proof.")
    for n, m in sorted(D['arms'].items()):
        if 'targets' in m:
            L.append(f"  - `{n}`: acquired **{m['targets']['acquired']} / 300 ({m['targets']['acquired'] / 300:.3f})**, per round {m['targets']['cum_acquired']}, pattern proofs {m['targets']['pattern_proofs']}, violations {m['targets']['violations']}, transfer {m['transfer']['acquired']} / 65, heldout greedy {m['heldout_greedy'][-1]:.3f}")
    for tag, c in D['coverage'].items():
        L.append(f"  - base reachability {tag} (`{c['file']}`): **{c['targets_with_pattern_proof']} / 300** targets with a strict proof at pass@10⁴, {c['pattern_hits']:,} hits ({c['rate_per_sample']:.2e} per sample), {c['solved_within_256']} within 256, solved without the pattern {c['solved_without_pattern']}; top per-target hits {c['per_target_hits'][:6]}")
    for tag, v in D['draws'].items():
        L.append(f"  - draw {tag} (f = {v['f']:g}): base-reachable {v['base_reachable']}, EI {v['ei_acquired']} = {v['ei_base_reachable']} base-reachable + **{v['ei_only']} EI-only**, frozen {v['frozen_acquired']}; EI / base {v['ei_over_base']:.2f}, EI / frozen {v['ei_over_frozen']:.2f}")
    for f, v in D['f_dial'].items():
        L.append(f"  - f = {f}: EI " + ', '.join(f"{k.split('/')[-1]} {x:.3f}" for k, x in v['ei'].items()) + (f" (mean {v['ei_mean']:.3f})" if v['ei_mean'] is not None else '') + "; frozen " + ', '.join(f"{x:.3f}" for x in v['frozen'].values()))
    return L


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
    covs = {'f0_c8_s0': 'artifacts/r5/cov_derived_ore_strict_f0_c8_s0_req.s0.jsonl', 'f0_c8_s1': 'artifacts/r5/cov_derived_ore_strict_f0_c8_s1_req.s0.jsonl'}
    for tag in ('f0_c8_s2', 'f0_c8_s3', 'f0_c8_s4', 'f0_c8_s5', 'f0.001_c8_s0', 'f0.001_c8_s1', 'f0.01_c8_s0', 'f0.01_c8_s1'):
        covs[tag] = f'artifacts/r3_2/cov_dore_{tag}.s0.jsonl'
    for tag, fn in covs.items():
        c = coverage(fn, 'derived_ore_strict')
        if c and c['targets'] == 300:
            D['coverage'][tag] = c
    # EI acquisition vs base reachability for the f = 0 draws (EI-only = acquired but not base-reachable at 1e4)
    D['draws'] = {}
    pairs = {'f0_c8_s0': ('artifacts/r5/ei_derived_ore_strict_f0_c8_s0_req', 'artifacts/r5/frozen_derived_ore_strict_f0_c8_s0_req'),
             'f0_c8_s1': ('artifacts/r5/ei_derived_ore_strict_f0_c8_s1_req', 'artifacts/r5/frozen_derived_ore_strict_f0_c8_s1_req'),
             'f0.01_c8_s0': ('artifacts/r5/ei_derived_ore_strict_f0.01_c8_s0_req', 'artifacts/r5/frozen_derived_ore_strict_f0.01_c8_s0_req'),
             'f0.01_c8_s1': ('artifacts/r5/ei_derived_ore_strict_f0.01_c8_s1_req', 'artifacts/r5/frozen_derived_ore_strict_f0.01_c8_s1_req')}
    for tag in ('f0_c8_s2', 'f0_c8_s3', 'f0_c8_s4', 'f0_c8_s5', 'f0.001_c8_s0', 'f0.001_c8_s1'):
        pairs[tag] = (f'artifacts/r3_2/ei_dore_{tag}', f'artifacts/r3_2/frozen_dore_{tag}')
    for tag, (ei, fr) in pairs.items():
        if tag in D['coverage'] and glob.glob(f'{ei}/round_*.json'):
            reach = set(D['coverage'][tag]['reachable_names']); got = solved_names(ei, 'derived_ore_strict')
            frn = solved_names(fr, 'derived_ore_strict') if glob.glob(f'{fr}/round_*.json') else set()
            r = len(reach)
            D['draws'][tag] = {'f': float(tag.split('_')[0][1:]), 'base_reachable': r, 'ei_acquired': len(got), 'ei_acq': len(got) / 300, 'ei_base_reachable': len(got & reach), 'ei_only': len(got - reach),
                               'frozen_acquired': len(frn), 'frozen_only': len(frn - reach), 'ei_over_base': len(got) / r if r else None, 'ei_over_frozen': len(got) / len(frn) if frn else None,
                               'base_rate_per_sample': D['coverage'][tag]['rate_per_sample'], 'source': [ei, fr, D['coverage'][tag]['file']]}
    D['f0_draws'] = {k: v for k, v in D['draws'].items() if v['f'] == 0}
    D['f_dial'] = {}
    for f, names in ((0, ['r5/ei_derived_ore_strict_f0_c8_s0_req', 'r5/ei_derived_ore_strict_f0_c8_s1_req', 'ei_dore_f0_c8_s2', 'ei_dore_f0_c8_s3', 'ei_dore_f0_c8_s4', 'ei_dore_f0_c8_s5']),
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
    for tag, v in D['draws'].items():
        print(f"  draw {tag}: base {v['base_reachable']} EI {v['ei_acquired']} (= {v['ei_base_reachable']} base-reachable + {v['ei_only']} EI-only) frozen {v['frozen_acquired']} EI/base {v['ei_over_base']} EI/frozen {v['ei_over_frozen']}")
    for f, v in D['f_dial'].items():
        print(f"  f = {f}: EI {v['ei']} frozen {v['frozen']}")
    with open(a.out.replace('.json', '_numbers.md'), 'w') as f:
        f.write('\n'.join(md_bullets(res)) + '\n')
    print('wrote', a.out, 'and', a.out.replace('.json', '_numbers.md'))
    if a.no_figs:
        return
    import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
    from matplotlib.lines import Line2D
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
    if D['draws'] or D['f_dial']:
        fig, ax = plt.subplots(figsize=(5.4, 4.2))
        MK = {'0': 'o', '0.001': 's', '0.01': '^'}; FC = {'0': '#2a78d6', '0.001': '#7aa6db', '0.01': '#eb6834'}
        for tag, v in D['draws'].items():
            fk = f"{v['f']:g}"
            ax.scatter([v['base_reachable'] / 300], [v['ei_acq']], marker=MK[fk], s=70, color=FC[fk], zorder=4)
            ax.scatter([v['base_reachable'] / 300], [v['frozen_acquired'] / 300], marker=MK[fk], s=50, facecolors='none', edgecolors=FC[fk], zorder=4)
            ax.annotate(tag.replace('_c8_', ' '), (v['base_reachable'] / 300, v['ei_acq']), textcoords='offset points', xytext=(5, 3), fontsize=6.5)
        ax.legend(handles=[Line2D([], [], marker=MK[k], color=FC[k], lw=0, label=f'f = {k} (filled EI, open frozen)') for k in MK], fontsize=7, frameon=False, loc='upper left')
        xs = [0, 0.3]; ax.plot(xs, xs, color='#b4b2ad', lw=1, ls=':'); ax.plot(xs, [2 * x for x in xs], color='#d9d7d2', lw=1, ls=':'); ax.plot(xs, [0.5 * x for x in xs], color='#d9d7d2', lw=1, ls=':')
        ax.set_xlabel('base strict reachability at pass@10⁴ (fraction of 300)'); ax.set_ylabel('EI acquisition after 8 rounds (fraction of 300)')
        ax.set_title('strict derived ORE, cap 8 (not a submission result): EI vs base reachability', fontsize=9)
        ax.spines[['top', 'right']].set_visible(False); ax.grid(color='#e8e7e3', lw=0.6); ax.set_axisbelow(True)
        ax.set_xlim(0, max(0.15, max([v['base_reachable'] / 300 for v in D['draws'].values()] + [0.1]) * 1.3)); ax.set_ylim(0, None)
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
