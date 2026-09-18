#!/usr/bin/env python3
"""Print the numbers.md tables for round3-run1 from artifacts/r3_1/summary.json (every number names its source file)."""
import json
S = json.load(open('artifacts/r3_1/summary.json'))
THR = {'depth3': 20, 'reductio': 12}
out = []
for pat in ('depth3', 'reductio'):
    P = S[pat]; D = P['draws']
    out.append(f'\n**{pat} — pre-RL rate per draw** (`artifacts/r3_1/cov_{pat}_s<seed>.s0.jsonl`, `coverage.py --k 2000 --temperature 0.8` on the 300 required targets = 600,000 samples per draw; hits = Σ per-proof `count` of verified proofs with `patterns.{pat}`; frozen@256 = targets whose first pattern proof has sample index ≤ 256):\n')
    out.append('| draw | pattern hits / 600k | rate | targets with a pattern proof | any verified proof (targets) | frozen@256 pattern targets | zero-rate |')
    out.append('|---|---|---|---|---|---|---|')
    for s in sorted(D, key=int):
        d = D[s]
        out.append(f'| s{s} | {d["hits"]} | {d["rate"]:.1e} | {d["targets_with_pattern"]} | {d["solved_any"]} | {d["frozen256_pattern_theorems"]} | {"yes" if d["zero_rate"] else "no"} |')
    out.append(f'\nn₀ = {P["n0"]} of {len(D)}.\n')
    out.append(f'**{pat} — arms** (`artifacts/r3_1/ei_{pat}_s<seed>_<arm>/found_<r>.jsonl`, start-index normalised, min-round rule, `patterns.{pat}` on the pruned proof; ignition = ≥ {THR[pat]} required targets with a pattern proof, cumulative; `nd_verify` re-run on 100 counted pattern proofs per arm or all if fewer):\n')
    out.append('| arm | zero-rate | ignition round | first pattern proof (round) | required targets with pattern proof, rounds 1–8 | required solved | required solved without pattern | neighbours solved / n | neighbours solved with pattern | held-out greedy r8 | verify fails / checked |')
    out.append('|---|---|---|---|---|---|---|---|---|---|---|')
    for k in sorted(P['arms'], key=lambda k: (int(k.split('_')[0][1:]), ['req', 'mix', 'drift'].index(k.split('_')[1]))):
        a = P['arms'][k]; s = k.split('_')[0][1:]
        z = 'yes' if D[s]['zero_rate'] else 'no'
        pr = [p['pattern_required'] for p in a['per_round']]
        out.append(f'| {k} | {z} | {a["ignition_round"] or "—"} | {a["first_pattern_round"] or "—"} | {pr} | {a["final_solved_required"]} | {len(a["required_solved_without_pattern"])} | '
                   f'{a["final_solved_neighbour"]} / {a["n_neighbour"]} | {a["final_pattern_neighbour"]} | {a["heldout_greedy_final"]:.3f} | {a["verify_failures"]} / {a["verify_sample"]} |')
    if P['drift']:
        out.append(f'\n**{pat} — drift arms, pattern rate on the required pool** (`artifacts/r3_1/dcov_{pat}_s<seed>_r<round>.s0.jsonl`, `coverage.py --k 1000` on the 300 required targets from the drift arm\'s round-r checkpoint = 300,000 samples; the drift arm trains on neighbours only with `--exclude_pattern {pat}`; excluded = found neighbour proofs with the pattern dropped from the mix, cumulative at round 8):\n')
        out.append('| draw | zero-rate | r2 hits (targets) | r4 | r6 | r8 | excluded proofs at r8 |')
        out.append('|---|---|---|---|---|---|---|')
        for s in sorted(P['drift'], key=int):
            d = P['drift'][s]; a = P['arms'].get(f's{s}_drift', {})
            ex = (a.get('per_round') or [{}])[-1].get('excluded_pattern_proofs')
            cells = [f'{d[r]["hits"]} / {d[r]["n_tried"]//1000}k ({d[r]["targets_with_pattern"]})' if r in d else '—' for r in ('2', '4', '6', '8')]
            out.append(f'| s{s} | {"yes" if D[s]["zero_rate"] else "no"} | ' + ' | '.join(cells) + f' | {ex} |')
print('\n'.join(out))
