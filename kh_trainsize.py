#!/usr/bin/env python3
"""cap-horizon: training-set term size (formula nodes over the pruned proof) per arm, including the
two inherited arms.  ds-composition's reviewer found the training-set mean term size tracked A4's
held-out damage better than the length histogram did, so proposal 10's request is answered for all
six arms here.
  python3 kh_trainsize.py > artifacts/kh/trainset_term_size.json
"""
import collections, gzip, json, os, statistics, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kh_size import term_size

SETS = [('K6', 6, 'data/p2/train_depth3_f0_a1.jsonl'),
        ('K8flat', 8, 'data/kh/train_K8flat_a3.jsonl.gz'),
        ('K8add', 8, 'data/kh/train_k8add.jsonl.gz'),
        ('K10', 10, 'data/kh/train_k10.jsonl.gz'),
        ('K12', 12, 'data/kh/train_k12.jsonl.gz'),
        ('K14', 14, 'data/kh/train_k14.jsonl.gz')]
out = {}
for arm, cap, fn in SETS:
    if not os.path.exists(fn):
        continue
    op = gzip.open if fn.endswith('.gz') else open
    ts, per_len = [], collections.defaultdict(list)
    n = 0
    for l in op(fn, 'rt'):
        r = json.loads(l)
        n += 1
        t = term_size(r['proof'])
        if t:
            ts.append(t[1]); per_len[t[0]].append(t[1])
    out[arm] = {'cap': cap, 'file': fn, 'records': n,
                'mean_term_size': round(statistics.mean(ts), 3),
                'median_term_size': statistics.median(ts), 'max_term_size': max(ts),
                'mean_pruned_length': round(statistics.mean([L for L, v in per_len.items() for _ in v]), 3),
                'by_length': {str(L): {'n': len(v), 'mean': round(statistics.mean(v), 2), 'max': max(v)} for L, v in sorted(per_len.items())}}
    print(arm, out[arm]['records'], 'mean term size', out[arm]['mean_term_size'], 'mean pruned length', out[arm]['mean_pruned_length'], file=sys.stderr, flush=True)
json.dump(out, open('artifacts/kh/trainset_term_size.json', 'w'), indent=1)
