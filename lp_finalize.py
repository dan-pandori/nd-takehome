#!/usr/bin/env python3
"""long-pool: attach Lean's verdict and term size on each label proof, drop any theorem whose label proof Lean rejects,
and draw the re-read subset.

  python3 lp_finalize.py --pool data/ladder/transfer_long.jsonl --lean artifacts/lp/lean_labels.jsonl \
      --rr_out data/ladder/transfer_long_rr600.jsonl --rr_per_bin 100
--lean is `lean_check.py --check <pool> --field minlen_proof --out ...` (rows in pool order, keyed by name).
The pool file is rewritten in place with `label_lean_ok` and `label_term_size`; the re-read subset is a seed-0 draw of
--rr_per_bin theorems per `L_true` bin (every theorem if a bin has fewer).
"""
import argparse, json, random, collections

ap = argparse.ArgumentParser()
ap.add_argument('--pool', required=True); ap.add_argument('--lean', required=True)
ap.add_argument('--rr_out', required=True); ap.add_argument('--rr_per_bin', type=int, default=100)
ap.add_argument('--seed', type=int, default=0)
a = ap.parse_args()
pool = [json.loads(l) for l in open(a.pool)]
lean = {r['name']: r for r in map(json.loads, open(a.lean))}
assert len(lean) == len(pool), (len(lean), len(pool))
keep, rej = [], []
for r in pool:
    v = lean[r['name']]
    r['label_lean_ok'] = bool(v['lean_ok']); r['label_term_size'] = v['size']
    (keep if v['lean_ok'] else rej).append(r)
with open(a.pool, 'w') as f:
    for r in keep:
        f.write(json.dumps(r) + '\n')
by = collections.defaultdict(list)
for r in keep:
    by[r['L_true']].append(r)
rng = random.Random(a.seed)
rr = []
for L in sorted(by):
    xs = sorted(by[L], key=lambda r: r['name']); rng.shuffle(xs); rr += xs[:a.rr_per_bin]
with open(a.rr_out, 'w') as f:
    for r in rr:
        f.write(json.dumps(r) + '\n')
print(json.dumps({'pool': len(keep), 'lean_rejected': [(r['name'], lean[r['name']]['lean_reason']) for r in rej],
                  'by_bin': {L: len(v) for L, v in sorted(by.items())}, 'rr': len(rr),
                  'rr_by_bin': dict(sorted(collections.Counter(r['L_true'] for r in rr).items()))}))
