#!/usr/bin/env python3
"""Which eval theorems the split hits are, per training source, order-free and order-sensitive keys."""
import json, glob, os, collections, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from splits import key, EVAL, R
ek = {n: {} for n in EVAL}; eko = {n: set() for n in EVAL}
for n, fn in EVAL.items():
    for l in open(fn):
        r = json.loads(l); ek[n][key(r['prompt'])] = r.get('name'); eko[n].add(key(r['prompt'], True))
src = {'p2_cap6': [f'{R}/data/p2/train_depth3_f0_a1.jsonl'], 'k12': [f'{R}/data/kh/train_k12.jsonl'],
       'rl_targets': [f'{R}/data/ladder/rl_targets.jsonl']}
for d in sorted(glob.glob(f'{R}/artifacts/bs/la_T1_*')): src[os.path.basename(d)] = sorted(glob.glob(f'{d}/mix_*.jsonl'))
out = {}
for s, fns in src.items():
    hit = collections.defaultdict(collections.Counter); ordered = collections.Counter(); ex = {}
    for fn in fns:
        for l in open(fn):
            pr = json.loads(l)['prompt']; k = key(pr)
            for n in ('tb72', 'dev1108', 'p2_heldout', 'holdout250', 'rr600', 'long2'):
                if k in ek[n]:
                    hit[n][ek[n][k]] += 1; ex.setdefault(ek[n][k], pr)
                    if key(pr, True) in eko[n]: ordered[n] += 1
    out[s] = {n: dict(c) for n, c in hit.items()}; out[s]['_ordered_records'] = dict(ordered); out[s]['_examples'] = ex
    print(s, {n: (len(c), sum(c.values())) for n, c in hit.items()}, 'ordered', dict(ordered), flush=True)
json.dump(out, open(f'{R}/review_bs/splits_detail.json', 'w'), indent=1)
