#!/usr/bin/env python3
"""Reviewer recount (compute-match), part 5: tables from my own recount json (r1 on cm12 / SN12 re-reads, r1 on best-cap12's
bucket files) + SN12 dev/h250/held inherited from best-state's eval summaries (same read.sh settings, labelled).
Per-seed values, means, deltas vs the pre-registered MDDs, stratified (per-arm) bootstrap 95 % CI of the mean difference,
paired cm12 - SN12 per seed.  Also proof length / term size of the shortest Lean-valid stored proof per solved target.
Term size (mine): number of inference nodes = ND lines that are not PR / AS / R (each AS-box counts once via its closing
rule).  Output: recount_tables.json + stdout."""
import json, os, random, subprocess, statistics as st, re
H = os.path.dirname(os.path.abspath(__file__))
A = json.load(open(f'{H}/recount_evals.json')); B = json.load(open(f'{H}/recount_evals_best12.json'))
inh = {}
for s in (0, 1, 2):
    for r in ('dev', 'h250', 'held'):
        d = json.loads(subprocess.run(['git', 'show', f'origin/dan_best-state:artifacts/bs/eval/T1_SN12_s{s}__{r}.json'],
                                      capture_output=True, text=True, check=True, cwd=H).stdout)
        inh[(s, r)] = d['solved'] if r != 'held' else d['rate']
def val(src, lab, r):
    d = src.get(f'{lab}__{r if r != "Q" else "rr600"}')
    if d is None: return None
    return {'tb72': d['lean_solved'], 'dev': d['lean_solved'], 'h250': d['lean_solved'], 'rr600': d['lean_solved'],
            'Q': d.get('Q'), 'long2': d['lean_solved'], 'held': d.get('rate')}[r]
Qs = ['tb72', 'dev', 'h250', 'Q', 'rr600', 'long2', 'held']
arms = {'best12': {q: [val(B, f'T1_best12_s{s}', 'held' if q == 'held' else q) for s in (0, 1, 2)] for q in Qs},
        'cm12': {q: [val(A, f'T1_cm12k64_s{s}', q) for s in (0, 1, 2)] for q in Qs},
        'SN12': {q: [val(A, f'T1_SN12_s{s}', q) if q in ('tb72', 'Q', 'rr600', 'long2') else inh[(s, q)] for s in (0, 1, 2)] for q in Qs}}
MDD = {'tb72': 6.5, 'dev': 61}
def boot(x, y, B=20000, seed=0):
    rng = random.Random(seed); v = sorted(st.mean(rng.choices(x, k=len(x))) - st.mean(rng.choices(y, k=len(y))) for _ in range(B))
    return [round(v[int(.025 * B)], 2), round(v[int(.975 * B) - 1], 2)]
out = {'arms': arms, 'contrasts': {}}
print('per seed (s0, s1, s2) and mean')
for q in Qs:
    print(q.ljust(6), '  '.join(f'{a} {arms[a][q]} mean {round(st.mean(arms[a][q]), 4)}' for a in arms))
for a, b in (('best12', 'cm12'), ('cm12', 'SN12'), ('best12', 'SN12')):
    for q in Qs:
        x, y = arms[a][q], arms[b][q]
        d = {'delta_mean': round(st.mean(x) - st.mean(y), 4), 'boot95': boot(x, y)}
        if a == 'cm12' and b == 'SN12': d['paired'] = [round(i - j, 4) for i, j in zip(x, y)]
        if q in MDD: d['MDD'] = MDD[q]; d['beyond_MDD'] = abs(d['delta_mean']) >= MDD[q]
        out['contrasts'][f'{a}-{b}:{q}'] = d; print(f'{a}-{b}', q, d)
json.dump(out, open(f'{H}/recount_tables.json', 'w'), indent=1)
