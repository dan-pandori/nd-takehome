#!/usr/bin/env python3
"""Decision-tree path length (tests on the path) per tf1200 state with tree_u_b3.json, and the tree's exactness on
tf1200 (held-out theorems; my template label).  -> out/tree_paths_tf1200.json (list), out/tree_tf1200_check.json"""
import json, os, sys, collections
HERE = os.path.dirname(os.path.abspath(__file__))
WS = os.path.expanduser('~/review/kalmar-complexity')
sys.path.insert(0, WS); sys.path.insert(0, os.path.join(WS, 'kalmar')); sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(WS, 'kalmar_complexity', 'programs', 'dtree'))
from state_env import decompose
from features import features, FEATS
from rv_dtree import my_label
trees = {f: json.load(open(os.path.join(WS, 'artifacts/kc/dtree', f)))['tree'] for f in ('tree_u_b3.json', 'tree_b3.json', 'tree_u_b1.json')}
paths, ok = [], collections.Counter()
n = 0
for line in open(os.path.join(WS, 'data/kalmar/tf1200_kal_sl.jsonl')):
    r = json.loads(line)
    kt = r['kal_tags']; kt = json.loads(kt.replace("'", '"')) if isinstance(kt, str) else kt
    steps, toks, env = decompose(r['prompt'], r['proof'], canon=True)
    for (st, act, h), tag in zip(steps, kt):
        F = features(list(st)); y = my_label(tag, list(act)); n += 1
        for name, t in trees.items():
            d = 0
            while t[0] == 'test':
                d += 1
                t = t[3] if str(F[t[1]]) == t[2] else t[4]
            ok[name] += t[1] == y
            if name == 'tree_u_b3.json':
                paths.append(d)
json.dump(paths, open(os.path.join(HERE, 'out', 'tree_paths_tf1200.json'), 'w'))
json.dump({'states': n, 'exact': dict(ok)}, open(os.path.join(HERE, 'out', 'tree_tf1200_check.json'), 'w'))
print(n, dict(ok))
