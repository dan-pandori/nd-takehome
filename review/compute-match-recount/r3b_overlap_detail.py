#!/usr/bin/env python3
"""Detail of r3 overlaps: the items, whether they also collide with premise ORDER kept (order-sensitive variant of my key),
and whether the eval item was solved by any read here.  Output: recount_splits_detail.json"""
import json, gzip, os, itertools
import r3_splits as R   # re-runs r3 at import (cheap enough); uses R.key
W = R.W
def okey(r):
    prem, c = R.parts(r); best = None
    for m in R.PERMS:
        f = lambda s: ' '.join(m.get(t, t) for t in s.split())
        k = ' , '.join(f(p) for p in prem) + ' |- ' + f(c)
        if best is None or k < best: best = k
    return best
tr = {}
for l in gzip.open('/tmp/cmr/train_k12.jsonl.gz', 'rt'):
    r = json.loads(l); tr.setdefault(R.key(r), []).append(('train_k12', r['thm'], okey(r)))
for l in open(f'{W}/data/ladder/rl_targets.jsonl'):
    r = json.loads(l); tr.setdefault(R.key(r), []).append(('rl_targets', r['thm'], okey(r)))
out = []
for ev, p in [('textbook72', 'data/bs/textbook72.jsonl'), ('dev1108', 'data/bs/dev1108.jsonl'), ('heldout5000', 'data/p2/heldout.jsonl'), ('transfer2285', 'data/ladder/transfer.jsonl')]:
    for l in open(f'{W}/{p}'):
        r = json.loads(l); k = R.key(r)
        if k in tr:
            out.append({'eval': ev, 'name': r['name'], 'thm': r.get('thm') or r['prompt'], 'eval_okey': okey(r),
                        'train': [{'src': s, 'thm': t, 'same_order': o == okey(r)} for s, t, o in tr[k][:3]]})
for x in out: print(json.dumps(x)[:400])
json.dump(out, open('recount_splits_detail.json', 'w'), indent=1)
