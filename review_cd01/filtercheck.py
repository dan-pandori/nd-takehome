#!/usr/bin/env python3
"""Reviewer (coe-dose01): prefilter rejections (dump rows with filter != null; Lean never saw them) sent to my Lean harness.
A pass would be a filter false reject (it can only lower counts).  Sample = dumpfilter.py's 1-in-200 draw of all
filter-rejected rows per ladder."""
import collections, json, sys
sys.path.insert(0, '/home/dan/work/coe-dose01/review_cd01')
from common import BIG, REPO, jl
import leanrc
out = {}
for stem in ('la_dose01_s0', 'la_dose01_s1', 'la_dose01_s2', 'la_ko_s1_r25-32'):
    rows = list(jl(f'{BIG}/dump/{stem}_filterrej.jsonl.gz'))
    items = sorted({(x['prompt'], x['lean_text']) for x in rows})
    r = leanrc.check(items)
    reasons = collections.Counter(x['filter'] for x in rows)
    out[stem] = dict(n=len(items), lean_accepted=sum(ok for ok, _ in r), filter_reasons=dict(reasons.most_common(8)))
    print(stem, out[stem], flush=True)
json.dump(out, open(f'{REPO}/review_cd01/out/filtercheck.json', 'w'), indent=1)
