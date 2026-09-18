#!/usr/bin/env python3
"""Reviewer tables for round3-run2 from artifacts/review_r3_2/arm_*.json, cov.json, r5_arms.json (+ a raw-record nd_verify pass).

Run from the phase-1 workspace: cd ~/review/round3-run2 && python3 <worktree>/review_r3_2_tables.py [rawverify]
"""
import json, os, sys, glob, re, random
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from review_run5_recount import rd, classify, normalise
from nd_verify import verify_text
OUT = f'{HERE}/artifacts/review_r3_2'
arm = {os.path.basename(f)[4:-5]: json.load(open(f)) for f in glob.glob(f'{OUT}/arm_*.json')}
cov = json.load(open(f'{OUT}/cov.json'))
r5 = json.load(open(f'{OUT}/r5_arms.json'))


def rawverify():
    """nd_verify on every raw (un-normalised) record of each arm's last found file, prompts taken from the pool file, plus my predicate."""
    res = {}
    for a, x in sorted(arm.items()):
        pool = {r['name']: r['prompt'] for r in rd(x['args']['targets'])}
        pat = 'reductio' if 'reductio' in a else 'derived_ore_strict'
        recs = rd(f"artifacts/r3_2/{a}/found_{x['rounds']}.jsonl")
        bad = nopat = wrongprompt = 0
        for r in recs:
            ok, _, nl = verify_text(pool[r['name']] + ' ' + r['proof'])
            c = classify(r['proof'])
            bad += (not ok) or c is None or nl != r['written']
            nopat += not (c and c[pat])
            wrongprompt += r['prompt'] != pool[r['name']]
        res[a] = {'raw_records': len(recs), 'verify_failures': bad, 'records_without_pattern': nopat, 'prompt_mismatch': wrongprompt}
        print(a, res[a], flush=True)
    json.dump(res, open(f'{OUT}/rawverify.json', 'w'), indent=1)


def tables():
    T = {}
    # ---- reductio
    rows = []
    for a in sorted(x for x in arm if 'reductio' in x):
        t, tr = arm[a]['targets'], arm[a]['transfer']
        bs = t['by_stratum']
        row = {'arm': a, 'rounds': arm[a]['rounds'], 'k': arm[a]['args']['k'], 'attempts': arm[a]['attempts_per_target'], 'seed': arm[a]['args']['seed'],
               'acquired': t['acquired'], 'solved': t['solved'], 'no_pattern': len(t['solved_without_pattern']),
               'by_stratum': {s: bs[s]['acquired'] for s in bs}, 'first_round': {s: bs[s]['first_proof_round'] for s in bs},
               'ignition_round': {s: bs[s]['ignition_round'] for s in bs},
               'at_round_8': {s: bs[s]['cum_acquired_by_round'][min(8, arm[a]['rounds']) - 1] for s in bs},
               'at_round_2': {s: bs[s]['cum_acquired_by_round'][1] for s in bs},
               'curve7': bs['7']['cum_acquired_by_round'], 'curve8': bs['8']['cum_acquired_by_round'], 'curve6': bs['6']['cum_acquired_by_round'],
               'curve9': bs['9']['cum_acquired_by_round'],
               'transfer_by_stratum': {s: v['acquired'] for s, v in tr['by_stratum'].items()}, 'transfer_acquired': tr['acquired'],
               'transfer_no_pattern': len(tr['solved_without_pattern']),
               'heldout_greedy_first_last': [arm[a]['heldout_greedy_by_round'][0], arm[a]['heldout_greedy_by_round'][-1]],
               'heldout_greedy_min': min(arm[a]['heldout_greedy_by_round']),
               'verified': t['verified'] + tr['verified'], 'verify_failures': t['verify_failures'] + tr['verify_failures'],
               'solved_matches_exec': arm[a]['solved_matches_exec'], 'round_field_agree': t['round_field_agrees_with_first_file'],
               'schemas_8_9': {k: v for k, v in t['by_schema_stratum(n,acquired)'].items() if k.split('|')[1] in ('8', '9', '10') and v[1] > 0}}
        rows.append(row)
    T['reductio'] = rows
    # frozen8 vs frozen16 (same seeds): are the first 8 rounds identical?
    for d in ('f0_s1_ss1', 'f0_s2_ss2'):
        a8, a16 = arm[f'frozen8_reductio_{d}']['targets'], arm[f'frozen16_reductio_{d}']['targets']
        T[f'frozen8_vs_frozen16_{d}'] = {'frozen8_cum': a8['cum_acquired_by_round'], 'frozen16_cum_first8': a16['cum_acquired_by_round'][:8]}
    # ---- derived-ORE
    drows = []
    covkey = {'ei_dore_f0.001_c8_s0': 'cov_dore_f0.001_c8_s0', 'ei_dore_f0.001_c8_s1': 'cov_dore_f0.001_c8_s1', 'ei_dore_f0_c8_s2': 'cov_dore_f0_c8_s2',
              'ei_dore_f0_c8_s3': 'cov_dore_f0_c8_s3', 'ei_dore_f0_c8_s4': 'cov_dore_f0_c8_s4', 'ei_dore_f0_c8_s5': 'cov_dore_f0_c8_s5'}
    def drow(label, f, ei_names, ei_cum, fr_names, base_names, tr_acq=None, held=None):
        ei, fr, base = set(ei_names), set(fr_names), (set(base_names) if base_names is not None else None)
        r = {'draw': label, 'f': f, 'ei': len(ei), 'ei_rate': round(len(ei) / 300, 4), 'frozen': len(fr), 'ei_over_frozen': round(len(ei) / max(1, len(fr)), 2),
             'ei_cum': ei_cum, 'frozen_not_in_ei': len(fr - ei)}
        if base is not None:
            r.update({'base_reach_1e4': len(base), 'ei_over_base': round(len(ei) / max(1, len(base)), 2), 'ei_only_vs_base': len(ei - base),
                      'ei_only_vs_base_and_frozen': len(ei - base - fr), 'base_not_in_ei': len(base - ei), 'frozen_not_in_base': len(fr - base)})
        if tr_acq is not None:
            r['transfer_acquired'] = tr_acq
        if held is not None:
            r['heldout_greedy_first_last'] = held
        return r
    for a, ck in covkey.items():
        fz = a.replace('ei_', 'frozen_')
        f = 0.001 if 'f0.001' in a else 0.0
        drows.append(drow(a[3:], f, arm[a]['targets']['acquired_names'], arm[a]['targets']['cum_acquired_by_round'], arm[fz]['targets']['acquired_names'],
                          cov[ck]['reach_names'], arm[a]['transfer']['acquired'], [arm[a]['heldout_greedy_by_round'][0], arm[a]['heldout_greedy_by_round'][-1]]))
    for s in ('s0', 's1'):
        e, fz = r5[f'ei_derived_ore_strict_f0_c8_{s}_req'], r5[f'frozen_derived_ore_strict_f0_c8_{s}_req']
        drows.append(drow(f'run5 dore_f0_c8_{s}', 0.0, e['acquired_names'], e['cum'], fz['acquired_names'], cov[f'cov_derived_ore_strict_f0_c8_{s}_req']['reach_names']))
        e, fz = r5[f'ei_derived_ore_strict_f0.01_c8_{s}_req'], r5[f'frozen_derived_ore_strict_f0.01_c8_{s}_req']
        drows.append(drow(f'run5 dore_f0.01_c8_{s}', 0.01, e['acquired_names'], e['cum'], fz['acquired_names'], cov[f'cov_dore_f0.01_c8_{s}']['reach_names']))
    T['dore'] = sorted(drows, key=lambda r: (r['f'], r['draw']))
    # rank correlation base reach vs EI over the f = 0 draws (n = 6)
    z = [(r['base_reach_1e4'], r['ei']) for r in T['dore'] if r['f'] == 0.0]
    T['dore_f0_base_vs_ei'] = z
    # ---- coverage six-line
    T['cov6'] = {k: {kk: v[kk] for kk in ('n_targets', 'solved_any', 'reach_pattern', 'samples_with_pattern')} for k, v in cov.items() if k.startswith('cov6')}
    # overlap six-line: base-reachable vs EI acquired by round 8 (C arms)
    T['r5_reductio_curves7'] = {a: v['by_stratum']['7'] for a, v in r5.items() if a.startswith('ei_reductio')}
    T['r5_reductio_seeds'] = {a: v['seed'] for a, v in r5.items() if a.startswith('ei_reductio')}
    json.dump(T, open(f'{OUT}/tables.json', 'w'), indent=1)
    for r in T['reductio']:
        print(r['arm'], r['attempts'], 'acq', r['acquired'], r['by_stratum'], 'first', r['first_round'], 'ign', r['ignition_round'], 'r8', r['at_round_8'], 'r2', r['at_round_2'])
        print('    c6', r['curve6']); print('    c7', r['curve7']); print('    c8', r['curve8']); print('    c9', r['curve9'])
        print('    transfer', r['transfer_acquired'], r['transfer_by_stratum'], 'held', r['heldout_greedy_first_last'], r['heldout_greedy_min'], 'vfail', r['verify_failures'], r['solved_matches_exec'], r['round_field_agree'])
        print('    schemas', r['schemas_8_9'])
    for k in T:
        if k.startswith('frozen8_vs'):
            print(k, T[k])
    for r in T['dore']:
        print(r)
    print(T['cov6']); print(T['r5_reductio_curves7']); print(T['r5_reductio_seeds'])


if __name__ == '__main__':
    rawverify() if len(sys.argv) > 1 and sys.argv[1] == 'rawverify' else tables()
