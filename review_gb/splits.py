#!/usr/bin/env python3
"""Reviewer: renaming-class disjointness between training files and evaluation pools (own canonicaliser).
Class key = min over all permutations of the atoms {P,Q,R,S} of (sorted premise strings, conclusion); F is falsum."""
import json, itertools, os, sys
ATOMS = ['P', 'Q', 'R', 'S']
def parts(prompt):
    body = prompt.split('THM', 1)[1].rsplit('PRF', 1)[0]
    pre, con = body.split(' SEQ ')
    toks = pre.split(); prem = []; cur = []; d = 0
    for t in toks:
        if t == ',' and d == 0: prem.append(' '.join(cur)); cur = []; continue
        d += (t == '(') - (t == ')'); cur.append(t)
    if cur: prem.append(' '.join(cur))
    return prem, con.strip()
def key(prompt):
    prem, con = parts(prompt)
    best = None
    for perm in itertools.permutations(ATOMS):
        m = dict(zip(ATOMS, perm))
        f = lambda s: ' '.join(m.get(t, t) for t in s.split())
        k = (tuple(sorted(f(p) for p in prem)), f(con))
        if best is None or k < best: best = k
    return best
def keys(path):
    ks = set(); n = 0
    for l in open(path):
        if not l.strip(): continue
        r = json.loads(l); n += 1
        ks.add(key(r['prompt']))
    return ks, n
H = os.path.expanduser('~/review/grpo-best/data')
train = {'k12_stage1': '/home/dan/work/best-state/data/kh/train_k12.jsonl', 'rl_targets': f'{H}/ladder/rl_targets.jsonl'}
evals = {'textbook72': f'{H}/bs/textbook72.jsonl', 'holdout250': f'{H}/bs/holdout250.jsonl', 'dev1108': f'{H}/bs/dev1108.jsonl',
         'heldout_p2': f'{H}/p2/heldout.jsonl', 'transfer': f'{H}/ladder/transfer.jsonl'}
K = {k: keys(v) for k, v in {**train, **evals}.items()}
for k, (s, n) in K.items(): print(f'{k:12s} records {n:7d} classes {len(s)}')
res = {}
for t in train:
    for e in evals:
        ov = len(K[t][0] & K[e][0]); res[f'{t}|{e}'] = ov
        print(f'{t:12s} x {e:11s} shared classes {ov}')
json.dump(res, open(os.path.expanduser('~/review/grpo-best/review_gb/splits.json'), 'w'), indent=0)
