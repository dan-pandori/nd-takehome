#!/usr/bin/env python3
"""Re-classify a written training set: counts of depth3 / reductio / derived_ore / derived_ore_strict on the
dependency-pruned proof (patterns.classify), plus max n_lines.  python f0_check.py FILE [FILE...]"""
import json, sys, os, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from patterns import classify
for fn in sys.argv[1:]:
    c = collections.Counter(); n = 0; mx = 0
    for l in open(fn):
        if not l.strip(): continue
        r = json.loads(l); n += 1; mx = max(mx, r['n_lines'])
        cl = classify(r['proof'])
        for p in ('depth3', 'reductio', 'derived_ore', 'derived_ore_strict', 'derived_dn'):
            c[p] += bool(cl[p])
    print(json.dumps({'file': fn, 'n': n, 'max_n_lines': mx, **c}), flush=True)
