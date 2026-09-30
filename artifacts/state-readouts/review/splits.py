# renaming-class disjointness: eval theorem variants under every injective atom map into P..U vs train theorems
import json, gzip, re, itertools, sys
AL='PQRSTU'
def norm(thm, m=None):
    lhs,rhs=thm.split('|-')
    prem=[];cur=[];d=0
    for t in lhs.split():
        if t=='(':d+=1
        if t==')':d-=1
        if t==',' and d==0: prem.append(' '.join(cur));cur=[];continue
        cur.append(t)
    if cur: prem.append(' '.join(cur))
    f=lambda s: re.sub(r'\b[A-EG-Z]\b', lambda x: m[x.group(0)], s) if m else s
    return (tuple(sorted(f(p) for p in prem)), f(rhs.strip()))
evals={'sc29':None,'tb':'data/sr/textbook_transfer.jsonl','tbl':'data/sr/textbook_long.jsonl'}
surv=set(l.strip() for l in open('data/sc/falsifier_survivors.txt') if l.strip())
E={}
for k,f in evals.items():
    recs=[json.loads(l) for l in open(f or 'data/sc/theorems.jsonl')]
    if k=='sc29': recs=[r for r in recs if r['name'] in surv]
    for r in recs:
        atoms=sorted(set(re.findall(r'\b[A-EG-Z]\b',r['thm'])))
        for img in itertools.permutations(AL,len(atoms)):
            E.setdefault(norm(r['thm'],dict(zip(atoms,img))),set()).add((k,r['name']))
print('eval variants',len(E),flush=True)
trains={'p2_a1 (S,SH stage1)':'/home/dan/review/state-env/data/p2/train_depth3_f0_a1.jsonl',
        'k12 (SN12 stage1 + EI retain)':'/home/dan/review/cap-horizon/data/kh/train_k12.jsonl.gz',
        'ladder rl_targets (T1 EI targets)':'data/ladder/rl_targets.jsonl'}
res={}
for tn,f in trains.items():
    op=gzip.open if f.endswith('.gz') else open
    n=0;hits=set()
    for l in op(f,'rt'):
        r=json.loads(l); n+=1
        h=E.get(norm(r['thm']))
        if h: hits|=h
    res[tn]={'n':n,'hits':sorted(hits)}
    print(tn,'n',n,'collisions',len(hits),sorted(hits)[:10],flush=True)
json.dump(res,open('rv/splits.json','w'),indent=1)
