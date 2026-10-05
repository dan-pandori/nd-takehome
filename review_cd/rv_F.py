#!/usr/bin/env python3
"""Reviewer: rebuild F(t) (every distinct Lean-accepted proof of t in any read, + references) and compare with the
executor's J1 targets (stage 1) and stage-2 targets.  Soundness: every target proof must come from a read (or be the
reference / a J2 proof).  Completeness: proofs in reads that are missing from the targets."""
import json, os, sys, glob, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rv_load as L
N = set(L.names())
F = collections.defaultdict(set)
nread = 0
for cap in (12, 6):
    for s in (0, 1, 2):
        for ck in L.PT + L.RL + ['r12', 'r16']:
            for pool in ('tb72', 'h250'):
                for x in (0, 1, 2):
                    d = L.read(cap, s, ck, pool, x)
                    if d is None:
                        continue
                    nread += 1
                    for n, v in d.items():
                        F[n].update(v[2])
for s in (0, 1, 2):
    for ck, x in (('pend', 4), ('r8', 4), ('r8', 10)):
        d = L.read(12, s, ck, 'C', x)
        nread += 1
        for n, v in d.items():
            F[n].update(v[2])
REF = {r['name']: r['proof'] for r in L.rows(os.path.expanduser('~/work/trajectory/data/tj/ref_targets.jsonl'))}
print('reads used', nread, 'refs', len(REF))
J2P = collections.defaultdict(lambda: collections.defaultdict(set))
for s in (0, 1, 2):
    for p in glob.glob(f'{L.CD}/j2/s{s}_*.jsonl'):
        for r in L.rows(p):
            J2P[s][r['name']].update(r.get('proofs') or [])
sets = json.load(open(f'{L.CD}/j1/sets.json'))
for s in (0, 1, 2):
    T = collections.defaultdict(set); srcs = {}
    for p in sorted(glob.glob(f'{L.CD}/j1/targets_s{s}_p*.jsonl')):
        for r in L.rows(p):
            T[r['name']].add(r['proof'])
    T2 = collections.defaultdict(set); T2j2 = collections.defaultdict(set)
    for r in L.rows(f'{L.CD}/j1/s2targets_s{s}.jsonl'):
        T2[r['name']].add(r['proof'])
        if r['tid'].startswith('j2:'):
            T2j2[r['name']].add(r['proof'])
    names = sets[str(s)]['H'] + sets[str(s)]['CAL']
    unexplained = sum(1 for n in T for p in T[n] if p not in F[n] and p != REF.get(n))
    missing = sum(1 for n in names for p in F[n] | ({REF[n]} if n in REF else set()) if p not in T[n])
    tot = sum(len(T[n]) for n in T)
    print(f's{s}: stage-1 targets {tot} over {len(T)} theorems (H+CAL {len(names)}; with no known proof: {len([n for n in names if not F[n] and n not in REF])}); '
          f'targets not in any read/ref: {unexplained}; read proofs missing from targets: {missing}')
    # stage 2: J2 proofs (all J2 files, any stage) that are not stage-1 targets vs stage-2 j2: rows
    newj2 = {(n, p) for n in J2P[s] for p in J2P[s][n] if p not in T[n] and n in set(names)}
    have = {(n, p) for n in T2j2 for p in T2j2[n]}
    print(f'     J2-found proofs not in stage 1: {len(newj2)}; scored in stage 2 as j2 rows: {len(have & newj2)}; '
          f'unscored: {len(newj2 - have)} on {len({n for n, p in newj2 - have})} theorems; stage-2 j2 rows not from J2 files: {len(have - newj2)}')
    unsc = collections.Counter(n for n, p in newj2 - have)
    print('     unscored J2 proofs per theorem:', dict(unsc))
