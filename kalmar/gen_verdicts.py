#!/usr/bin/env python3
"""Pre-registered "generalises" verdicts (run kalmar-pretrain).  For each test set and KAL-D seed: KAL-D's greedy rate on
the set over its in-distribution greedy rate (tf1200) at the set's atom mix; >= 0.7 -> generalises (if it also beats the
control's pass@32 by more than the MDD), < 0.3 -> does not generalise, between -> partially.

  python3 kalmar/gen_verdicts.py > artifacts/kalmar/gen_verdicts.txt
"""
import collections, gzip, json, statistics as st

A = 'artifacts/kalmar'
S = json.load(open(f'{A}/summary.json'))
sets = {'G1 (premise lines supplied)': ('data/kalmar/g1_premises.jsonl', 'g1_supplied_greedy', None),
        'G2 larger formulas': ('data/kalmar/g2_large.jsonl', 'g2_large_greedy', 'g2_large'),
        'G3 classical': ('data/kalmar/g3_classical.jsonl', 'g3_classical_greedy', 'g3_classical'),
        'hand_proved_14': ('data/kalmar/hand_proved_14_kal_sl.jsonl', 'hand_proved_14_greedy', 'hand_proved_14'),
        '>= 17 (ge17)': ('data/kalmar/ge17_kal_sl.jsonl', 'ge17_greedy', 'ge17')}
for lab, (fn, fg, solve_key) in sets.items():
    atoms = collections.Counter(json.loads(l)['n_atoms'] for l in open(fn))
    n = sum(atoms.values())
    ratios, rates = [], []
    for s in range(3):
        indist = S['free']['KAL-D']
        base = sum(atoms[a] * indist[f'atoms={a}']['valid'][s] for a in atoms) / n
        rows = [json.loads(l) for l in gzip.open(f'{A}/free/kalD_s{s}__{fg}.rows.jsonl.gz', 'rt')]
        r = sum(x['valid'] for x in rows) / len(rows)
        rates.append(r); ratios.append(r / base if base else None)
    line = f"{lab:28s} KAL-D greedy {', '.join(f'{100 * x:.1f}' for x in rates)} %; ratio to in-distribution " \
           f"{', '.join(f'{x:.2f}' for x in ratios)}"
    if solve_key:
        for read in ('plain', 'logical'):
            kd = S['solve']['KAL-D'][read][solve_key]['pass@32']; ct = S['solve']['control'][read][solve_key]['pass@32']
            mdd = 3.04 * ((st.variance(kd) + st.variance(ct)) / 2) ** 0.5
            line += f" | {read} pass@32 diff {st.mean(kd) - st.mean(ct):+.1f} (MDD {mdd:.1f})"
    v = 'generalises' if min(ratios) >= 0.7 else 'does not generalise' if max(ratios) < 0.3 else 'partially'
    print(line + f" -> {v} (by the ratio)")
