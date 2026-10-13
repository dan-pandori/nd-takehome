#!/usr/bin/env python3
"""create-or-elicit: the 1 % dose arm against the knockout and full arms (Addendum 5; descriptive, plus exploratory exact
tests that were not pre-registered), from the comparison and per-round files.

  python3 coe/coe_dose_summary.py --out artifacts/coe/dose_summary.json
"""
import argparse, json, os
from scipy.stats import boschloo_exact, fisher_exact, mannwhitneyu


def arm_rows(d, arm):
    return {k: v for k, v in d['seeds'].items() if v['arm'] == arm}


def rounds(arm, seed):
    stem = {'full': 'la_full_s', 'ko': 'la_ko_s', 'dose1': 'la_dose1_s'}[arm]
    fn = f'artifacts/coe/rounds/{stem}{seed}.json'
    if arm == 'full' and seed < 3:
        fn = f'artifacts/coe/rounds/old_full_s{seed}.json'
    if not os.path.exists(fn):
        return None
    d = json.load(open(fn))
    pr, st = d['per_round'], d.get('sigma_subtypes_by_round', {})
    rs = sorted(int(r) for r in pr if int(r) <= 16)
    free = {r: sum(v for k, v in st.get(str(r), {}).items() if k and k.startswith('pos_free')) for r in rs}
    sig = {r: sum(v for k, v in d.get('proof_classes_by_round', {}).get(str(r), {}).items() if k == 'sigma') for r in rs}
    return {'last_round': rs[-1], 'strict_targets_cum': {r: pr[str(r)]['sigma_targets_cum'] for r in rs},
            'free_positive_reductio': free, 'sigma_proofs': sig,
            'heldout_first_solved': len([r for r in d.get('heldout_first_solve_round', {}).values() if int(r) <= 16])}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', required=True)
    a = ap.parse_args()
    r16 = json.load(open('artifacts/coe/compare_r16_x0.json'))
    pend = json.load(open('artifacts/coe/compare_pend_x0.json'))
    out = {'seeds': {}}
    for arm in ('full', 'ko', 'dose1'):
        for k, v in arm_rows(r16, arm).items():
            p = pend['seeds'].get(k, {})
            out['seeds'][k] = {'arm': arm, 'seed': v['seed'], 'r16_strict_solved': v['strict_heldout_solved'],
                               'r16_acquired': v['acquired'], 'r16_per_family': v['per_family'],
                               'pend_strict_solved': p.get('strict_heldout_solved'), 'pend_acquired': p.get('acquired'),
                               'rounds': rounds(arm, v['seed'])}
    S = out['seeds']
    by = {arm: [x for x in S.values() if x['arm'] == arm] for arm in ('full', 'ko', 'dose1')}
    tests = {}
    d, k, f = by['dose1'], by['ko'], by['full']
    if d:
        acq = lambda xs: sum(1 for x in xs if x['r16_acquired'])
        tests['dose_vs_ko_acquired'] = {'dose1': f'{acq(d)}/{len(d)}', 'ko': f'{acq(k)}/{len(k)}',
                                        'boschloo_p': float(boschloo_exact([[acq(d), len(d) - acq(d)], [acq(k), len(k) - acq(k)]], alternative='greater').pvalue),
                                        'fisher_p': float(fisher_exact([[acq(d), len(d) - acq(d)], [acq(k), len(k) - acq(k)]], alternative='greater')[1])}
        xs = [x['r16_strict_solved'] for x in d]
        tests['dose_vs_ko_members'] = {'dose1': xs, 'ko': [x['r16_strict_solved'] for x in k],
                                       'mann_whitney_p': float(mannwhitneyu(xs, [x['r16_strict_solved'] for x in k], alternative='greater', method='exact').pvalue)}
        tests['dose_vs_full_members'] = {'dose1': xs, 'full': [x['r16_strict_solved'] for x in f],
                                         'mann_whitney_two_sided_p': float(mannwhitneyu(xs, [x['r16_strict_solved'] for x in f], alternative='two-sided', method='exact').pvalue)}
        during = lambda x: [fam for fam in x['r16_acquired'] if fam not in (x['pend_acquired'] or [])]
        tests['acquired_during_rl'] = {key: {x['seed']: during(x) for x in by[key]} for key in by}
    out['tests'] = tests
    out['note'] = ('Exploratory: the dose arm is described in Addendum 5, not tested; these tests were added at the end of '
                   'the run. Plain k 256, x0, Lean alone; strict sigma-covered held-out members (106).')
    json.dump(out, open(a.out, 'w'), indent=1)
    for kk, v in S.items():
        r = v['rounds'] or {}
        print(kk, 'pend', v['pend_strict_solved'], 'r16', v['r16_strict_solved'], v['r16_acquired'],
              'r1 targets', (r.get('strict_targets_cum') or {}).get(1), 'r1 free', (r.get('free_positive_reductio') or {}).get(1),
              'r1 sigma', (r.get('sigma_proofs') or {}).get(1))
    print(json.dumps(tests, indent=1))


if __name__ == '__main__':
    main()
