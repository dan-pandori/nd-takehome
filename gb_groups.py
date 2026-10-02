#!/usr/bin/env python3
"""grpo-best: trajectory's groups (A end-of-pretraining solves, B r8-only, C neither; sample seed 0) per seed, and the
EI baselines the pre-registration needs, from trajectory's per-theorem read-outs (artifacts/gb/ei_eval/, bucket
trajectory/artifacts/tj/eval/).  -> artifacts/gb/groups.json + a table on stdout."""
import json, os, statistics, sys
E = 'artifacts/gb/ei_eval'
def solved(s, ck, x):
    out = {}
    for p in ('tb72', 'h250'):
        for l in open(f'{E}/s{s}_{ck}__{p}_x{x}.jsonl'):
            r = json.loads(l); out[r['name']] = r['n_ok']
    return out
groups, rows = {}, []
for s in (0, 1, 2):
    pe, r8 = solved(s, 'pend', 0), solved(s, 'r8', 0)
    g = {n: ('A' if pe[n] else 'B' if r8[n] else 'C') for n in pe}
    groups[s] = g
    C = [n for n in g if g[n] == 'C']
    row = {'seed': s, 'A': sum(v == 'A' for v in g.values()), 'B': sum(v == 'B' for v in g.values()), 'C': len(C)}
    for ck in ('r2', 'r4', 'r8'):
        for x in (0, 1):
            v = solved(s, ck, x)
            row[f'C_{ck}_x{x}'] = sum(1 for n in C if v[n])
            row[f'all_{ck}_x{x}'] = sum(1 for n in v if v[n])
        u = solved(s, ck, 0); w = solved(s, ck, 1)
        row[f'C_{ck}_either'] = sum(1 for n in C if u[n] or w[n])
    rows.append(row)
os.makedirs('artifacts/gb', exist_ok=True)
json.dump({'groups': {str(s): g for s, g in groups.items()}, 'ei': rows}, open('artifacts/gb/groups.json', 'w'), indent=0)
keys = list(rows[0])
print(' '.join(f'{k:>11}' for k in keys))
for r in rows:
    print(' '.join(f'{r[k]:>11}' for k in keys))
