#!/usr/bin/env python3
"""Arm F's training pool: the union of the four noise-floor pools, de-duplicated by atom-renaming
class (`key`), and checked disjoint from the held-out set by the same class.

  python3 sd_pool.py --pools data/nf/train_p1.jsonl ... --heldout data/p2/heldout.jsonl \
                     --out data/sd/train_fresh.jsonl --report data/sd/pool_fresh.json

Records are kept in pool order (p1 first); the first record of each class wins.  Also reports the
per-length composition of the surviving set, since the control's set is flat 31,000 per length 2-6.
"""
import argparse, json, collections, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gen import canon_key


def key_of(r):
    return r.get('key') or canon_key(r['thm'].strip())


ap = argparse.ArgumentParser()
ap.add_argument('--pools', nargs='+', required=True)
ap.add_argument('--heldout', required=True)
ap.add_argument('--out', required=True)
ap.add_argument('--report', required=True)
a = ap.parse_args()

hk = set()
for l in open(a.heldout):
    if l.strip():
        hk.add(key_of(json.loads(l)))

seen = set()
per_pool = {}
kept_len = collections.Counter()
dropped_dup = collections.Counter()
heldout_hits = 0
n_in = 0
with open(a.out, 'w') as fo:
    for p in a.pools:
        k0, n0 = len(seen), 0
        for l in open(p):
            if not l.strip():
                continue
            r = json.loads(l)
            n0 += 1
            n_in += 1
            k = key_of(r)
            if k in hk:
                heldout_hits += 1
                continue
            if k in seen:
                dropped_dup[p] += 1
                continue
            seen.add(k)
            kept_len[r['n_lines']] += 1
            fo.write(json.dumps(r) + '\n')
        per_pool[p] = {'records': n0, 'new_classes': len(seen) - k0, 'dup_of_earlier': dropped_dup[p]}

rep = {'pools': per_pool, 'records_in': n_in, 'records_out': len(seen),
       'distinct_classes': len(seen), 'dropped_duplicate_class': n_in - len(seen) - heldout_hits,
       'dropped_heldout_class_collision': heldout_hits,
       'heldout_classes': len(hk), 'by_n_lines': dict(sorted(kept_len.items())),
       'out': a.out}
json.dump(rep, open(a.report, 'w'), indent=1)
print(json.dumps(rep, indent=1))
