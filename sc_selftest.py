#!/usr/bin/env python3
"""Does this run's judging path accept proofs the base model demonstrably produced?

Feeds every proof in a ladder_ei `found_transfer_*.jsonl` (written by the same base checkpoint, judged by the
Lean gate) through THIS run's judging path -- `normalize.norm` then `lean_judge.judge_many`, exactly what
support.py does -- and reports any that come back rejected.  A rejection here means support.py under-counts.
"""
import sys, json, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from normalize import norm
from lean_judge import judge_many

fn = sys.argv[1]
want = set(open(sys.argv[2]).read().split()) if len(sys.argv) > 2 else None
recs = [json.loads(l) for l in open(fn) if l.strip()]
if want:
    recs = [r for r in recs if (r.get('name') or r.get('thm')) in want]
pairs = [(r['prompt'], norm(r['proof'])) for r in recs]
res = judge_many(pairs)
bad = [(recs[i]['name'], res[i][1]) for i, (ok, _, _) in enumerate(res) if not ok]
print(f'{len(recs)} proofs from {fn}: accepted {len(recs)-len(bad)}, REJECTED {len(bad)}')
for n, why in bad[:10]:
    print('  REJECTED', n, why)
# also: does the un-normalised proof pass?
res2 = judge_many([(r['prompt'], r['proof']) for r in recs])
print(f'un-normalised: accepted {sum(1 for ok,_,_ in res2 if ok)}/{len(recs)}')
