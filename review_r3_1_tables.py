#!/usr/bin/env python3
"""Markdown tables for review_round3-run1.md from artifacts/review_r3_1/*.json (reviewer's recount)."""
import json, os
O = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'artifacts', 'review_r3_1')
cov = json.load(open(f'{O}/cov.json')); dcov = json.load(open(f'{O}/dcov.json')); ex = json.load(open(f'{O}/extra.json'))
L = lambda v: ' '.join(str(x) for x in v) if v is not None else '—'
for pat in ['depth3', 'reductio']:
    print(f'\n**{pat}: pre-RL sample and arms (required stratum = targets with a verified {pat} proof, cumulative r1…r8)**\n')
    print('| seed | pre-RL hits / 600k (targets) | frozen@256 targets | `req` r1…r8 | `mix` required r1…r8 | ign. round req / mix | `mix` neighbours solved r8 (with pattern) | first pattern proof in `mix`: neighbour / required round | transfer r8 req / mix | held-out greedy r8 req / mix / drift (of 5000) |')
    print('|---|---|---|---|---|---|---|---|---|---|')
    for s in range(20, 28):
        c = cov[f'cov_{pat}_s{s}']
        a = {k: json.load(open(f'{O}/arm_ei_{pat}_s{s}_{k}.json')) for k in ['req', 'mix', 'drift']}
        e = {k: ex[f'ei_{pat}_s{s}_{k}'] for k in ['req', 'mix', 'drift']}
        z = ' **(zero-rate)**' if c['pattern_hits'] == 0 else ''
        print(f"| {s}{z} | {c['pattern_hits']} ({c['pattern_targets']}) | {c['frozen256_pattern_targets']} | {L(a['req']['required_pattern_cum'])} | {L(a['mix']['required_pattern_cum'])} | "
              f"{a['req']['ignition_round'] or '—'} / {a['mix']['ignition_round'] or '—'} | {a['mix']['neighbour_solved_cum'][-1]} ({a['mix']['neighbour_pattern_cum'][-1]}) | "
              f"{e['mix']['nb_first_pattern_round'] or '—'} / {e['mix']['first_required_pattern_round'] or '—'} | {e['req']['transfer_pattern_cum']} / {e['mix']['transfer_pattern_cum']} | "
              f"{a['req']['heldout_greedy'][-1]} / {a['mix']['heldout_greedy'][-1]} / {a['drift']['heldout_greedy'][-1]} |")
    print(f'\n**{pat}: drift arms (neighbours only, pattern proofs excluded from training)**\n')
    print('| seed | neighbours solved r1…r8 | neighbour targets with a pattern proof r1…r8 | excluded proofs (round json) r1…r8 | required-pool hits / 300k (targets) at r2, r4, r6, r8 |')
    print('|---|---|---|---|---|')
    for s in range(20, 28):
        c = cov[f'cov_{pat}_s{s}']; a = json.load(open(f'{O}/arm_ei_{pat}_s{s}_drift.json'))
        z = ' **(zero-rate)**' if c['pattern_hits'] == 0 else ''
        dc = [dcov.get(f'dcov_{pat}_s{s}_r{r}') for r in (2, 4, 6, 8)]
        print(f"| {s}{z} | {L(a['neighbour_solved_cum'])} | {L(a['neighbour_pattern_cum'])} | {L(a['excluded_pattern_proofs_json'])} | " + (', '.join(f"{d['pattern_hits']} ({d['pattern_targets']})" for d in dc) if all(dc) else 'not sampled') + ' |')
tot = {'raw': 0, 'vf': 0, 'arms': 0, 'dist': 0}
for f in os.listdir(O):
    if f.startswith('arm_'):
        a = json.load(open(f'{O}/{f}')); tot['raw'] += a['raw_records']; tot['vf'] += a['verify_fail']; tot['arms'] += 1; tot['dist'] += a['distinct_norm_proofs']
        assert all(x == y for x, y in a['cum_check'].values()) and a['args_ok'] and not a['unknown_name'] and not a['prompt_mismatch'] and not a['unparsed'], f
print('\n', tot)
