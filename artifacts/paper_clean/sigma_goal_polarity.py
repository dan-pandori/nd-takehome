#!/usr/bin/env python3
"""paper-clean item 1: is sigma (DN on a NOT-NOT G built by NEGI from AS NOT G; patterns.reductio) ever applied to a
negated goal G in the full pretraining set D?  Counts sigma lines and records by the polarity of G.
  python3 artifacts/paper_clean/sigma_goal_polarity.py /home/dan/work/capability-defs/data/kh/train_k12.jsonl"""
import json, sys, os, collections
sys.path.insert(0, os.getcwd())
from patterns import parse

def sigma_lines(lines):
    byidx = {ln['idx']: ln for ln in lines}
    out = []
    for ln in lines:
        if ln['rule'] != 'DN' or not ln['refs']:
            continue
        neg = byidx.get(ln['refs'][0])
        if not neg or neg['rule'] != 'NEGI' or len(neg['refs']) != 2:
            continue
        hyp = byidx.get(neg['refs'][0])
        if hyp and hyp['rule'] == 'AS' and hyp['formula'] == ('not', ln['formula']):
            out.append(ln['formula'])
    return out

c = collections.Counter()
for row in open(sys.argv[1]):
    r = json.loads(row)
    lines = parse(r['proof'])
    if lines is None:
        c['unparsable'] += 1; continue
    s = sigma_lines(lines)
    if not s:
        continue
    c['records_with_sigma'] += 1
    negs = [isinstance(g, tuple) and g[0] == 'not' for g in s]
    c['sigma_lines'] += len(s)
    c['sigma_lines_negated_G'] += sum(negs)
    c['records_with_sigma_on_negated_G'] += any(negs)
    c['records_with_sigma_only_on_negated_G'] += all(negs)
print(json.dumps(dict(c), indent=1))
