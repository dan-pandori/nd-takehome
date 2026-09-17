#!/usr/bin/env python3
"""Run-4 self-check: re-verify every proof in a found_<r>.jsonl against its prompt with nd_verify, count
start-index-normalised distinct proofs and depth-3 theorems (patterns.classify on the pruned proof).
  python3 run4_check.py artifacts/r4/<arm>/found_8.jsonl [more files]
Pure Python (no torch)."""
import sys, json, os, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from nd_verify import verify_text
from normalize import norm
from patterns import classify

for fn in sys.argv[1:]:
    recs = [json.loads(l) for l in open(fn) if l.strip()]
    bad = 0; seen = set(); d3 = set(); thms = set(); per_round = collections.Counter(); first = {}
    depth_hist = collections.Counter()
    for x in recs:
        ok, reason, nl = verify_text(x['prompt'] + ' ' + x['proof'])
        if not ok or nl != x['written']:
            bad += 1
            if bad <= 3: print('  BAD', reason, x['name'], x['proof'][:80])
        pn = norm(x['proof']); k = (x['name'], pn)
        thms.add(x['name'])
        if k in seen: continue
        seen.add(k)
        cl = classify(pn)
        if cl and cl['depth3']:
            d3.add(x['name']); first[x['name']] = min(first.get(x['name'], 99), x['round'])
    for n, r in first.items(): per_round[r] += 1
    cum = 0; curve = []
    for r in range(1, 9):
        cum += per_round[r]; curve.append(cum)
    print(f'{fn}: records {len(recs)}, verify failures {bad}, distinct normalised proofs {len(seen)}, theorems solved {len(thms)}, '
          f'depth-3 theorems {len(d3)} (cumulative by first round {curve})')
