#!/usr/bin/env python3
"""Reviewer recount (compute-match), part 3: split disjointness by renaming class (my own key: atoms permuted over all
24 maps of {P,Q,R,S}, premises sorted as a multiset, min string).  Training side: train_k12 (Stage-1 data and ladder
replay) and rl_targets (the ladder trains on its own proofs of them).  Evaluation side: every pool read here.
Also an order-free check that ignores premises entirely is NOT done (premise order matters only via the sort).  Output: recount_splits.json"""
import json, gzip, itertools, os, re
W = os.path.expanduser('~/review/compute-match')
AT = 'PQRS'; PERMS = [dict(zip(AT, p)) for p in itertools.permutations(AT)]
def parts(r):
    if 'thm' in r and r['thm']:
        lhs, c = r['thm'].split('|-'); prem = [p.strip() for p in lhs.split(' , ')] if lhs.strip() else []
    else:
        m = re.fullmatch(r'THM ?(.*?) ?SEQ (.*) PRF', r['prompt'].strip()); prem = [p.strip() for p in m.group(1).split(' , ')] if m.group(1).strip() else []; c = m.group(2)
    return prem, c.strip()
def key(r):
    prem, c = parts(r); best = None
    for m in PERMS:
        f = lambda s: ' '.join(m.get(t, t) for t in s.split())
        k = ' , '.join(sorted(f(p) for p in prem)) + ' |- ' + f(c)
        if best is None or k < best: best = k
    return best
def keys(fn):
    op = gzip.open if fn.endswith('.gz') else open
    return {key(json.loads(l)) for l in op(fn, 'rt')}
train = {'train_k12': keys('/tmp/cmr/train_k12.jsonl.gz'), 'rl_targets': keys(f'{W}/data/ladder/rl_targets.jsonl')}
evals = {n: keys(f'{W}/{p}') for n, p in [('textbook72', 'data/bs/textbook72.jsonl'), ('dev1108', 'data/bs/dev1108.jsonl'),
         ('holdout250', 'data/bs/holdout250.jsonl'), ('heldout5000', 'data/p2/heldout.jsonl'), ('rr600', 'data/ladder/transfer_long_rr600.jsonl'),
         ('long2', 'data/ladder/transfer_long2.jsonl'), ('transfer2285', 'data/ladder/transfer.jsonl')]}
out = {'sizes': {k: len(v) for k, v in {**train, **evals}.items()}, 'overlap': {}}
for a, A in train.items():
    for b, B in evals.items():
        out['overlap'][f'{a} x {b}'] = len(A & B)
print(json.dumps(out, indent=1))
json.dump(out, open(os.path.join(os.path.dirname(__file__), 'recount_splits.json'), 'w'), indent=1)
