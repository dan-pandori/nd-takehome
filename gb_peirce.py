#!/usr/bin/env python3
"""grpo-best: of the group-C theorems each arm solves at r8 (either sample seed, pooled seeds), how many have an accepted
proof of the Peirce shape (a reductio whose refutation builds an implication by explosion: BOTE inside, DN at the end)?
-> table on stdout."""
import json
G = {int(s): g for s, g in json.load(open('artifacts/gb/groups.json'))['groups'].items()}
def f(arm, s, x, pool):
    return (f'artifacts/gb/ei_eval/s{s}_r8__{pool}_x{x}.jsonl' if arm == 'EI' else f'artifacts/gb/eval/gb_{arm}_s{s}_r8__{pool}_x{x}.jsonl')
print('arm        C solved   with a Peirce-shape proof')
for arm in ('EI', 'default', 'unlikely', 'passk'):
    tot = pe = 0
    for s in (0, 1, 2):
        C = {n for n, g in G[s].items() if g == 'C'}
        sol = {}
        for x in (0, 1):
            for pool in ('tb72', 'h250'):
                for l in open(f(arm, s, x, pool)):
                    r = json.loads(l)
                    if r['name'] in C and r['n_ok']:
                        sol.setdefault(r['name'], []).extend(r['proofs'])
        tot += len(sol); pe += sum(1 for ps in sol.values() if any(' BOTE ' in p and ' DN ' in p for p in ps))
    print(f'{arm:<10}{tot:>9}{pe:>12}')
