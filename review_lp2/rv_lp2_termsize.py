#!/usr/bin/env python3
"""Reviewer (long-pool-2): term sizes of every counted pool proof vs the pool's upper-bound proof (lean_check reports)."""
import json, collections
S=[json.loads(l) for l in open('rv/lean/allpool.jsonl')]
L=[json.loads(l) for l in open('rv/lean/allpool_lean.jsonl')]
U={}
for s,l in zip([json.loads(x) for x in open('rv/lean/sample.jsonl')],[json.loads(x) for x in open('rv/lean/sample_lean.jsonl')]):
    if s['arm']=='UB': U[s['name'].split('|')[1]]=l['size']
pool={}
for f in ('data/ladder/transfer_long2.jsonl','data/ladder/transfer_long2_calib.jsonl'):
    for l in open(f):
        r=json.loads(l); pool[r['name']]=r
def st(r): return '17' if r['stageE']=='exact17' else '>=18'
print('rejected', sum(1 for l in L if not l['lean_ok']), 'of', len(L))
mins=collections.defaultdict(dict)
for s,l in zip(S,L):
    tag,name,_=s['name'].split('|'); fam=tag.rsplit('_s',1)[0]
    d=mins[fam]; d[name]=min(d.get(name,999), l['size'])
for fam,d in sorted(mins.items()):
    by=collections.defaultdict(list); below=eq=0
    for n,ts in d.items():
        by[st(pool[n])].append(ts); below+=ts<U[n]; eq+=ts==U[n]
    print(f'{fam:10s} per-theorem min term size by stratum (n, median, min):', {k:(len(v), sorted(v)[len(v)//2], min(v)) for k,v in sorted(by.items())},
          f'| model min < ub_proof size on {below}/{len(d)}, equal on {eq}')
ub=collections.defaultdict(list)
for n,r in pool.items(): ub[st(r)].append(U[n])
print('ub_proof term size by stratum (n, median, min, max):', {k:(len(v), sorted(v)[len(v)//2], min(v), max(v)) for k,v in sorted(ub.items())})
