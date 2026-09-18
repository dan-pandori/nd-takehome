#!/usr/bin/env python3
"""round3-run1 analysis: pre-RL rates per draw, per-arm per-round acquisition per stratum, ignition, route choice, drift rates.

  python r3_1_analysis.py            # -> artifacts/r3_1/summary.json, artifacts/r3_1/summary_table.md

Counts: from found_<r>.jsonl (start-index normalised, min-round rule via phase2_metrics.arm_metrics), patterns.classify on the
normalised proof; nd_verify re-run on every counted pattern proof (--verify_all) or on a 100-proof sample per arm (default).
Strata by target name: depth-3 required d3req_*, neighbours d3nb_*; reductio required targets_reductio_req_*, neighbours rnb_*.
"""
import argparse, json, os, sys, glob, collections, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from phase2_metrics import arm_metrics, rd
from ignition_analysis import coverage_stats
from patterns import classify
from normalize import norm
from nd_verify import verify_text

A = 'artifacts/r3_1'
THR = {'depth3': 20, 'reductio': 12}
SEEDS = list(range(20, 28))
REQ = {'depth3': 'data/r3_1/depth3_req.jsonl', 'reductio': 'data/r3_1/reductio_req.jsonl'}


def stratum(name):
    return 'required' if name.startswith(('d3req_', 'targets_reductio_req_')) else 'neighbour'


def arm_summary(arm, pattern, verify_all=False):
    rows = arm_metrics(arm, pattern)
    if not rows:
        return None
    targets = rd(json.load(open(f'{arm}/args.json'))['targets'])
    n_str = collections.Counter(stratum(t['name']) for t in targets)
    per = []
    for x in rows:
        pat_req = [n for n in x['pattern_names_targets'] if stratum(n) == 'required']
        pat_nb = [n for n in x['pattern_names_targets'] if stratum(n) == 'neighbour']
        sol_req = [n for n in x['solved_names_targets'] if stratum(n) == 'required']
        sol_nb = [n for n in x['solved_names_targets'] if stratum(n) == 'neighbour']
        st = json.load(open(f"{arm}/round_{x['round']}.json"))
        per.append({'round': x['round'], 'pattern_required': len(pat_req), 'pattern_neighbour': len(pat_nb),
                    'solved_required': len(sol_req), 'solved_neighbour': len(sol_nb),
                    'solved_required_without_pattern': len(set(sol_req) - set(pat_req)),
                    'solved_neighbour_without_pattern': len(set(sol_nb) - set(pat_nb)),
                    'pattern_proofs': x['n_pattern_proofs_targets'], 'transfer_pattern': x['acq_transfer_theorems'],
                    'transfer_solved': x['transfer_solved'], 'heldout_greedy': x['heldout_greedy'],
                    'mix_rl_records': st.get('mix_rl_records', 0), 'excluded_pattern_proofs': st.get('excluded_pattern_proofs'),
                    'excluded_pattern_theorems': st.get('excluded_pattern_theorems')})
    last = rows[-1]
    ign = next((p['round'] for p in per if p['pattern_required'] >= THR[pattern]), None)
    first = next((p['round'] for p in per if p['pattern_required'] > 0), None)
    first_nb_success = next((p['round'] for p in per if p['solved_neighbour'] > 0), None)
    # re-verify counted pattern proofs (final cumulative file), route-choice list of required targets solved without the pattern
    fn = f'{arm}/found_{last["round"]}.jsonl'
    recs = rd(fn)
    by_thm = collections.defaultdict(list)
    for x in recs:
        by_thm[x['name']].append(x)
    pat_proofs = [(x['prompt'], norm(x['proof'])) for x in recs if stratum(x['name']) == 'required' and (classify(norm(x['proof'])) or {}).get(pattern)]
    sample = pat_proofs if verify_all else random.Random(0).sample(pat_proofs, min(100, len(pat_proofs)))
    nfail = sum(not verify_text(p + ' ' + s)[0] for p, s in sample)
    nopat = sorted(set(last['solved_names_targets']) & {n for n in by_thm if stratum(n) == 'required'} - set(last['pattern_names_targets']))
    return {'arm': arm, 'rounds_done': last['round'], 'n_required': n_str['required'], 'n_neighbour': n_str['neighbour'],
            'per_round': per, 'ignition_round': ign, 'first_pattern_round': first, 'first_neighbour_success_round': first_nb_success,
            'final_pattern_required': per[-1]['pattern_required'], 'final_solved_required': per[-1]['solved_required'],
            'final_pattern_neighbour': per[-1]['pattern_neighbour'], 'final_solved_neighbour': per[-1]['solved_neighbour'],
            'required_solved_without_pattern': nopat, 'verify_sample': len(sample), 'verify_failures': nfail,
            'heldout_greedy_final': last['heldout_greedy'], 'examples': last['pattern_examples_targets'][:3]}


def drift_rates(pattern, s):
    out = {}
    for r in (2, 4, 6, 8):
        fn = f'{A}/dcov_{pattern}_s{s}_r{r}.s0.jsonl'
        if os.path.exists(fn):
            c = coverage_stats(fn, pattern)
            out[str(r)] = {'n_targets': c['n_targets'], 'n_tried': c['n_tried'], 'hits': c['hits_pattern'], 'rate': c['rate_pattern'],
                           'targets_with_pattern': c['targets_with_pattern'], 'solved_any': c['solved_any']}
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--verify_all', action='store_true')
    a = ap.parse_args()
    summ = {}
    for pattern in ('depth3', 'reductio'):
        P = {'draws': {}, 'arms': {}, 'drift': {}}
        for s in SEEDS + ([1, 2] if pattern == 'reductio' else []):
            fn = f'{A}/cov_{pattern}_s{s}.s0.jsonl'
            if os.path.exists(fn):
                c = coverage_stats(fn, pattern)
                P['draws'][str(s)] = {'n_targets': c['n_targets'], 'n_tried': c['n_tried'], 'hits': c['hits_pattern'], 'rate': c['rate_pattern'],
                                      'targets_with_pattern': c['targets_with_pattern'], 'distinct_pattern_proofs': c['distinct_pattern_proofs'],
                                      'frozen256_pattern_theorems': c['frozen256_pattern_theorems'], 'frozen256_solved_any': c['frozen256_solved_any'],
                                      'solved_any': c['solved_any'], 'zero_rate': c['hits_pattern'] == 0,
                                      'top_targets': c['per_target'][:5]}
            for arm in ('req', 'mix', 'drift'):
                d = f'{A}/ei_{pattern}_s{s}_{arm}'
                if os.path.isdir(d):
                    r = arm_summary(d, pattern, a.verify_all)
                    if r:
                        P['arms'][f's{s}_{arm}'] = r
            dr = drift_rates(pattern, s)
            if dr:
                P['drift'][str(s)] = dr
        P['n0'] = sum(d['zero_rate'] for d in P['draws'].values())
        summ[pattern] = P
    json.dump(summ, open(f'{A}/summary.json', 'w'), indent=1)
    # table
    L = []
    for pattern in ('depth3', 'reductio'):
        P = summ[pattern]
        L.append(f'\n## {pattern}: pre-RL rate per draw (k = 2,000 x required targets), n0 = {P["n0"]}\n')
        L.append('| draw | tried | pattern hits | rate | targets w/ pattern | frozen@256 pattern thms | solved any |')
        L.append('|---|---|---|---|---|---|---|')
        for s, d in P['draws'].items():
            L.append(f'| s{s} | {d["n_tried"]} | {d["hits"]} | {d["rate"]:.2e} | {d["targets_with_pattern"]} | {d["frozen256_pattern_theorems"]} | {d["solved_any"]} |')
        L.append(f'\n## {pattern}: arms (threshold {THR[pattern]} required targets)\n')
        L.append('| arm | zero-rate | ignition round | first pattern round | first nb success | pattern required per round | solved required | solved nb | req solved w/o pattern | verify fail |')
        L.append('|---|---|---|---|---|---|---|---|---|---|')
        for k, r in P['arms'].items():
            s = k.split('_')[0][1:]
            z = P['draws'].get(s, {}).get('zero_rate')
            L.append(f'| {k} | {z} | {r["ignition_round"]} | {r["first_pattern_round"]} | {r["first_neighbour_success_round"]} | '
                     f'{[p["pattern_required"] for p in r["per_round"]]} | {r["final_solved_required"]} | {r["final_solved_neighbour"]}/{r["n_neighbour"]} | '
                     f'{len(r["required_solved_without_pattern"])} | {r["verify_failures"]}/{r["verify_sample"]} |')
        if P['drift']:
            L.append(f'\n## {pattern}: drift arms, pattern rate on the required pool (k = 1,000 x 300)\n')
            L.append('| draw | r2 hits | r4 | r6 | r8 |')
            L.append('|---|---|---|---|---|')
            for s, d in P['drift'].items():
                L.append(f'| s{s} | ' + ' | '.join(f'{d[r]["hits"]}/{d[r]["n_tried"]}' if r in d else '-' for r in ('2', '4', '6', '8')) + ' |')
    open(f'{A}/summary_table.md', 'w').write('\n'.join(L) + '\n')
    print('\n'.join(L))


if __name__ == '__main__':
    main()
