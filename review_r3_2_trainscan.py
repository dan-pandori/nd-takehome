#!/usr/bin/env python3
"""Reviewer: count pattern proofs (pruned and unpruned predicate) in the Stage-1 training files used by round3-run2."""
import json, sys, os, collections
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from review_run5_recount import classify, normalise
out = {}
for fn in sys.argv[1:]:
    c = collections.Counter(); ex = []
    for l in open(fn):
        x = json.loads(l); k = classify(normalise(x['proof'])); c['n'] += 1
        if k is None:
            c['unparsable'] += 1; continue
        for p in ('reductio', 'reductio_unpruned', 'derived_ore_strict', 'derived_ore_strict_unpruned', 'derived_ore_loose'):
            c[p] += bool(k[p])
        c['DN_rule_used'] += ': DN ' in x['proof']
    out[os.path.basename(fn)] = dict(c); print(os.path.basename(fn), dict(c), flush=True)
json.dump(out, open(f'{HERE}/artifacts/review_r3_2/trainscan.json', 'w'), indent=1)
