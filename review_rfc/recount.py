#!/usr/bin/env python3
"""Reviewer recount (rl-from-ckpt), written for this review; nothing imported from rfc_*.py / tj_*.py.
Reads the raw per-theorem read-outs (state_eval jsonl) of this run and of `trajectory` (end arm + starts),
checks completeness and per-record consistency, and writes solved sets + counts + per-stratum truncation."""
import json, glob, os, collections, sys
R = os.path.expanduser('~/review/rl-from-ckpt'); E = f'{R}/artifacts/rfc/eval'
TJ = os.path.expanduser('~/review/trajectory/artifacts/tj/eval')
OUT = f'{R}/review_rfc/rv'; os.makedirs(OUT, exist_ok=True)
POOLS = {p: [json.loads(l)['name'] for l in open(f'{R}/data/bs/{f}.jsonl')] for p, f in (('tb72', 'textbook72'), ('h250', 'holdout250'))}
STARTS = ['p1600', 'p5000', 'p12000', 'p16000']
def rd(fn): return [json.loads(l) for l in open(fn) if l.strip()]
bad = []; solved = {}; trunc = {}; nproofs = {}
def load(key, fn, pool):
    rows = rd(fn); names = [r['name'] for r in rows]
    if sorted(names) != sorted(POOLS[pool]): bad.append((key, 'names'))
    for r in rows:
        if r['n_tried'] != 256: bad.append((key, r['name'], 'n_tried', r['n_tried']))
        if r['n_ok'] != r['n_tried'] - len(r['reasons']): bad.append((key, r['name'], 'n_ok'))
        if r['solved'] != bool(r['proofs']): bad.append((key, r['name'], 'solved'))
        if r['solved'] != (r['n_ok'] > 0): bad.append((key, r['name'], 'n_ok>0'))
    solved[key] = sorted(r['name'] for r in rows if r['solved'])
    nproofs[key] = sum(len(r['proofs']) for r in rows)
    # truncation strings: env 'action truncated' / 'step cap'
    tr = sum(1 for r in rows for x in r['reasons'] if 'action truncated' in x or 'step cap' in x)
    trunc[key] = (tr, 256 * len(rows))
    return rows
expect = []
for s in (0, 1, 2):
    for st in STARTS:
        for ck in ('r2', 'r4', 'r8'):
            for p in POOLS:
                for x in (0, 1): expect.append((f'L s{s} {st} {ck} {p} x{x}', f'{E}/s{s}_{st}_{ck}__{p}_x{x}.jsonl', p))
    for st in STARTS + ['pend']:
        for p in POOLS:
            for x in (0, 1): expect.append((f'C s{s} {st} r8 {p} x{x}', f'{E}/c{s}_{st}_r8__{p}_x{x}.jsonl', p))
    # trajectory: starts (r0) and end arm
    for ck in STARTS + ['p0', 'pend', 'r2', 'r4', 'r8']:
        for p in POOLS:
            for x in (0, 1): expect.append((f'T s{s} {ck} {p} x{x}', f'{TJ}/s{s}_{ck}__{p}_x{x}.jsonl', p))
for st in STARTS:
    for p in POOLS: expect.append((f'RR s0 {st} {p} x1', f'{E}/s0_{st}_rr__{p}_x1.jsonl', p))
missing = [k for k, f, p in expect if not os.path.exists(f)]
for k, f, p in expect:
    if os.path.exists(f): load(k, f, p)
extra = sorted(set(glob.glob(f'{E}/*.jsonl')) - {f for _, f, _ in expect})
print('expected', len(expect), 'missing', missing, 'extra', [os.path.basename(x) for x in extra])
print('record inconsistencies', len(bad), bad[:10])
json.dump({'solved': solved, 'trunc': trunc, 'nproofs': nproofs}, open(f'{OUT}/recount.json', 'w'))
# counts table
def n(k): return len(solved[k]) if k in solved else None
print('\n## solved counts (k 256)')
for x in (0, 1):
    print(f'\nsample seed x{x}: start | ladder r2 tb/h | r4 tb/h | r8 tb/h | control r8 tb/h | start(r0, trajectory) tb/h')
    for st in STARTS + ['pend']:
        for s in (0, 1, 2):
            if st == 'pend':
                row = [f"{n(f'T s{s} r{c} tb72 x{x}')}/{n(f'T s{s} r{c} h250 x{x}')}" for c in (2, 4, 8)]
            else:
                row = [f"{n(f'L s{s} {st} r{c} tb72 x{x}')}/{n(f'L s{s} {st} r{c} h250 x{x}')}" for c in (2, 4, 8)]
            row.append(f"{n(f'C s{s} {st} r8 tb72 x{x}')}/{n(f'C s{s} {st} r8 h250 x{x}')}")
            row.append(f"{n(f'T s{s} {st} tb72 x{x}')}/{n(f'T s{s} {st} h250 x{x}')}")
            print(f'{st} s{s} | ' + ' | '.join(row))
print('\n## re-read of seed-0 starts (x1) vs trajectory start x1')
for st in STARTS:
    for p in POOLS:
        a = set(solved[f'RR s0 {st} {p} x1']); b = set(solved[f'T s0 {st} {p} x1'])
        print(st, p, 'rr', len(a), 'tj', len(b), 'only rr', len(a - b), 'only tj', len(b - a))
print('\n## truncation per read (frac of samples; >0.1% flagged)')
hi = [(k, t / m) for k, (t, m) in trunc.items() if t / m > 0.001]
print(len(hi), 'of', len(trunc), 'reads > 0.1 %;  max', sorted(hi, key=lambda z: -z[1])[:12])
