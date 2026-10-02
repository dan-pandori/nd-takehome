#!/usr/bin/env python3
"""Reviewer: reproduce recheck.py's flip-control draw and show the disjunctions in the 8 passing flips."""
import json, glob, os, random, sys, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rlean
R = os.path.expanduser('~/review/trajectory-cap6'); E = f'{R}/artifacts/tj6/eval'
rd = lambda fn: [json.loads(l) for l in open(fn) if l.strip()]
rng = random.Random(20261002); ARMS = collections.defaultdict(list); REJ = collections.defaultdict(list)
for fn in sorted(glob.glob(f'{E}/s?_*__*_x?.jsonl')):
    b = os.path.basename(fn)[:-6]; s, ck = b.split('__')[0].split('_'); xs = b[-2:]
    arm = f'{s}_{ck}' if ck in ('pend', 'r8') and xs == 'x0' else (f'{s}_mid' if ck not in ('p0', 'pend', 'r8') and xs == 'x1' else None)
    for r in rd(fn):
        fe = r.get('fail_example') or ''
        if fe.startswith('LEANREJ '): REJ[s].append((r['prompt'], fe[8:]))
        if arm:
            for p in r['proofs']: ARMS[arm].append((r['prompt'], p, b, r['name']))
pool = ARMS['s0_r8']; unt = rng.sample(pool, 60); rej = rng.sample(REJ['s0'] + REJ['s1'] + REJ['s2'], 60)
flip = [x for x in rng.sample(pool, 800) if 'ORI' in x[1]][:60]
rr = rlean.check([(p, rlean.render(p, b, flip=('Or.inl', 'Or.inr'))) for p, b, _, _ in flip])
for x, (o, _, _) in zip(flip, rr):
    if o: print([part.split(' : ')[0].split(None, 1)[1].strip(' |') + ' ' + part.split(' : ')[1] for part in x[1].split(' ; ') if ' : ORI' in part])
