#!/usr/bin/env python3
"""Reviewer's renaming-class disjointness: training file(s) vs evaluation pools (own canonicaliser)."""
import json, itertools, re, sys
def split_prompt(p):
    p = p.strip()
    if p.startswith('THM'): p = ' ' + p[3:-3].strip(); prem, concl = p.split(' SEQ ')
    else: prem, concl = p.split(' |- ')
    # split premises on top-level commas
    ps, depth, cur = [], 0, []
    for t in prem.split():
        if t == ',' and depth == 0: ps.append(' '.join(cur)); cur = []; continue
        depth += (t == '(') - (t == ')'); cur.append(t)
    if cur: ps.append(' '.join(cur))
    return [x for x in ps if x], concl.strip()
def canon(prem, concl):
    best = None
    for perm in itertools.permutations(prem) if len(prem) <= 4 else [tuple(prem)]:
        m = {}; out = []
        for t in (' , '.join(perm) + ' |- ' + concl).split():
            if re.fullmatch(r'[PQRS]', t): t = m[t] if t in m else m.setdefault(t, 'ABCD'[len(m)])
            out.append(t)
        s = ' '.join(out); best = s if best is None or s < best else best
    return best
def keys(fn, field_prompt=('prompt', 'thm')):
    ks = set(); n = 0
    for l in open(fn):
        if not l.strip(): continue
        r = json.loads(l); n += 1
        p = r.get('prompt') or r.get('thm')
        ks.add(canon(*split_prompt(p)))
    return ks, n
TRAIN = ['/home/dan/nd-takehome/data/p2/train_depth3_f0_a1.jsonl']
EVAL = ['data/sc/theorems.jsonl', 'data/p2/heldout.jsonl']
T = {}
for f in TRAIN + EVAL: T[f] = keys(f); print(f, 'records', T[f][1], 'classes', len(T[f][0]), flush=True)
res = {}
for a in TRAIN:
    for b in EVAL: res[f'{a} x {b}'] = len(T[a][0] & T[b][0])
res['heldout x transfer'] = len(T[EVAL[0]][0] & T[EVAL[1]][0])
print(json.dumps(res, indent=1)); json.dump(res, open('rev_sf/splits.json', 'w'), indent=1)
