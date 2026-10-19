#!/usr/bin/env python3
"""Reviewer: for each executor ledger row, is every number in `value` present in `quote`? (IDs only; phase-1 safe.)
Numbers are normalised (thousands separators dropped; 1e-6 / 10^{-6} kept as text). A row fails if any value number
is absent from the quote's number set -> such values are derived/interpreted and need a manual check in phase 2."""
import csv, glob, re, json, os
num = re.compile(r'\d+(?:[.,]\d+)*')
def nums(s):
    out = set()
    for m in num.findall(s):
        x = m.replace(',', '')
        out.add(x.rstrip('0').rstrip('.') if '.' in x else x)
    return out
res = {}
for f in sorted(glob.glob('/home/dan/work/rl-compute-share/rl_compute_share/ledger/*.tsv')):
    rows = list(csv.DictReader(open(f), delimiter='\t', quoting=csv.QUOTE_NONE))
    fail = [r['claim_id'] for r in rows if nums(r['value']) - nums(r['quote'])]
    withnum = sum(1 for r in rows if nums(r['value']))
    res[os.path.basename(f)] = dict(rows=len(rows), value_has_number=withnum, number_not_in_quote=len(fail), ids=fail)
json.dump(res, open('out/valuecheck.json', 'w'), indent=1)
for k, v in res.items(): print(k, {kk: vv for kk, vv in v.items() if kk != 'ids'})
