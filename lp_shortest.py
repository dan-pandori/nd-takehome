#!/usr/bin/env python3
"""long-pool: collect the fewest-step accepted proof of every (model, solved theorem) in artifacts/lp/rr/*.jsonl for a Lean
term-size pass:  python3 lp_shortest.py > artifacts/lp/rr_shortest.jsonl ; python3 lean_check.py --check artifacts/lp/rr_shortest.jsonl --out artifacts/lp/rr_shortest_lean.jsonl"""
import json, glob, os
def steps(p):
    ls = [x.strip() for x in p.split(';') if x.strip() and x.strip() != 'QED']
    return sum(1 for l in ls if not l.endswith(': PR'))
for fn in sorted(glob.glob('artifacts/lp/rr/*.jsonl')):
    m = os.path.basename(fn)[:-6]
    for l in open(fn):
        r = json.loads(l)
        if r['solved']:
            p = min(r['proofs'], key=lambda x: (steps(x), x))
            print(json.dumps({'name': f"{m}|{r['name']}", 'prompt': r['prompt'], 'proof': p, 'steps': steps(p)}))
