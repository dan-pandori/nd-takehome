#!/usr/bin/env python3
"""Decision-tree path length (number of tests) for every tf1200 state (run kalmar-complexity, Q4 predictor).

  python3 kalmar_complexity/q4_tree_paths.py  -> artifacts/kc/q4/tree_paths_tf1200.json (list aligned with
  q4_states.py's order; tree = artifacts/kc/dtree/tree_u_b3.json; also checks the tree's template is right)"""
import json, os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT); sys.path.insert(0, os.path.join(ROOT, 'kalmar_complexity/programs/dtree'))
from state_env import decompose
from features import features, label, FEATS
T = json.load(open(os.path.join(ROOT, 'artifacts/kc/dtree/tree_u_b3.json')))['tree']
out, ok = [], 0
for line in open(os.path.join(ROOT, 'data/kalmar/tf1200_kal_sl.jsonl')):
    r = json.loads(line)
    kt = r['kal_tags']; kt = json.loads(kt.replace("'", '"')) if isinstance(kt, str) else kt
    steps, toks, env = decompose(r['prompt'], r['proof'], canon=True)
    for (st, act, hs), tag in zip(steps, kt):
        F = features(st); x = [str(F[k]) for k in FEATS]
        t, d = T, 0
        while t[0] == 'test':
            t = t[3] if x[FEATS.index(t[1])] == t[2] else t[4]; d += 1
        ok += t[1] == label(tag, act)
        out.append(d)
json.dump({'tree': 'artifacts/kc/dtree/tree_u_b3.json', 'paths': out, 'exact': ok, 'states': len(out)},
          open(os.path.join(ROOT, 'artifacts/kc/q4/tree_paths_tf1200.json'), 'w'))
print('tf1200 states', len(out), 'tree exact', ok)
