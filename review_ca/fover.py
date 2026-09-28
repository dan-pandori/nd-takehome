import json, sys, collections
from splits import key, split_prem
from rvload import SL
B={}
for l in open('../data/ca/heldout_B.jsonl'):
    r=json.loads(l); B.setdefault(key(r['thm']),[]).append(r)
hit={}
exact=0
for l in open('/tmp/rv_ca/data/train_fresh.jsonl'):
    t=json.loads(l); k=key(t['thm'])
    if k in B:
        b=B[k][0]; hit[b['name']]=(b['n_lines'], b['pat']['depth3'], b['thm'], t['thm'], t.get('key')==b.get('key'))
print('B theorems overlapping train_fresh:', len(hit), 'depth3:', sum(v[1] for v in hit.values()), 'by len', collections.Counter(v[0] for v in hit.values()), 'same gen key (i.e. executor-visible):', sum(v[4] for v in hit.values()))
for n,v in list(hit.items())[:4]: print(n, v)
json.dump(sorted(hit), open('b_overlap_F.json','w'))
