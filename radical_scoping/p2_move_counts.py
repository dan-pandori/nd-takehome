"""P2 skill-knockout feasibility: per-rule usage in the cap-6 Stage-1 training set (data/train.jsonl, 154,990 ND proofs,
the set the lean_seq 3.2M models are rendered from) and in the eval pools. Stdout is a table."""
import json, sys, collections
def load(p):
    return [json.loads(l) for l in open(p)]
def rules_of(r):
    if 'rules' in r: return set(r['rules'])
    pf = r.get('proof') or ''
    return {t.split()[0] for t in pf.split(' : ')[1:]} if pf else set()
paths = sys.argv[1:]
for p in paths:
    rows = load(p)
    c = collections.Counter(); n = len(rows); has = 0
    for r in rows:
        rs = rules_of(r)
        if rs: has += 1
        c.update(rs)
    print(f'\n## {p}  n={n}  with_rules={has}')
    for k, v in sorted(c.items(), key=lambda x: -x[1]):
        print(f'{k:8s} {v:7d} {100*v/max(has,1):6.2f}%')
