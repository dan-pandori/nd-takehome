#!/usr/bin/env python3
"""Reviewer (grpo-state): split disjointness by renaming class, own canonical key: premises and conclusion from the
prompt, every permutation of the atoms {P,Q,R,S} applied, premises sorted as a multiset, minimum over permutations."""
import json, itertools, os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__))
ATOMS = ['P', 'Q', 'R', 'S']
def parse(prompt):
    m = re.fullmatch(r'THM ?(.*?) ?SEQ (.*) PRF', prompt.strip())
    lhs = m.group(1).strip(); return ([p.strip() for p in lhs.split(' , ')] if lhs else []), m.group(2).strip()
def key(prompt):
    prem, c = parse(prompt); best = None
    for perm in itertools.permutations(ATOMS):
        mp = dict(zip(ATOMS, perm))
        f = lambda s: ' '.join(mp.get(t, t) for t in s.split())
        k = (tuple(sorted(f(p) for p in prem)), f(c))
        best = k if best is None or k < best else best
    return best
def rd(fn): return [json.loads(l) for l in open(fn) if l.strip()]
train = {'rl_targets': 'data/ladder/rl_targets.jsonl'}
evals = {'transfer': 'data/ladder/transfer.jsonl', 'heldout_p2': 'data/p2/heldout.jsonl', 'heldout_root': 'data/heldout.jsonl',
         'transfer_long2': 'data/ladder/transfer_long2.jsonl', 'transfer_long2_calib': 'data/ladder/transfer_long2_calib.jsonl',
         'rr600': 'data/ladder/transfer_long_rr600.jsonl', 'ge17': 'data/ladder/transfer_long_ge17.jsonl', 'validation_36': None}
K = {}
for n, fn in {**train, **evals}.items():
    if fn is None: continue
    K[n] = {key(r['prompt']) for r in rd(fn)}
# validation_36: thm field only
v = [json.loads(l) for l in open('targets/validation_36.jsonl')]
def thm2prompt(t):
    l, r = t.split('|-'); return f"THM {l.strip()} SEQ {r.strip()} PRF".replace('THM  SEQ', 'THM SEQ')
K['validation_36'] = {key(thm2prompt(x['thm'].strip())) for x in v}
out = {'sizes': {n: len(s) for n, s in K.items()}}
for t in train:
    for e in evals:
        out[f'{t} & {e}'] = len(K[t] & K[e])
for a, b in itertools.combinations(['transfer', 'heldout_p2', 'transfer_long2', 'transfer_long2_calib', 'rr600', 'ge17'], 2):
    out[f'{a} & {b}'] = len(K[a] & K[b])
print(json.dumps(out, indent=1)); json.dump(out, open(f'{HERE}/splits.json', 'w'), indent=1)
