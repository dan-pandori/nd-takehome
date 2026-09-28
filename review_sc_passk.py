#!/usr/bin/env python3
"""Reviewer: pass@k per stratum done properly (unbiased for k<=n, labelled extrapolation for k>n)."""
import json, glob, collections, os
from fractions import Fraction
rows=[]
for f in sorted(glob.glob('artifacts/sc/s*.jsonl')):
    if 'secondary' in f: continue
    for l in open(f):
        if l.strip(): rows.append(json.loads(l))
THMS=[json.loads(l) for l in open('data/sc/theorems.jsonl')]
NAMES=[t['name'] for t in THMS]; L={t['name']:t['L_true'] for t in THMS}
by=collections.defaultdict(dict)
for r in rows: by[(r['stage'],r['model'],r['seed'],r['temperature'])][r['name']]=r

def passk_unb(n,c,k):
    if c==0: return 0.0
    if n-c<k: return 1.0
    num=Fraction(1)
    for i in range(k): num*=Fraction(n-c-i,n-i)
    return float(1-num)

def passk(r,k):
    n,c=r['n_tried'],r['n_ok']
    if k<=n: return passk_unb(n,c,k),False
    p=c/n
    return 1-(1-p)**k, True   # extrapolation beyond n (only happens for early-stopped, i.e. easy, theorems)

strata=collections.defaultdict(list)
for n in NAMES: strata[L[n]].append(n)
KS=[32,100,320,1000,3200,10000]
for seed in (0,1):
    st='s1' if seed==0 else 's3'
    print(f'=== pass@k, stage {st}, Stage-1 seed {seed}, T=0.8 (base | EI); * = some theorems extrapolated past n ===')
    print(f"   {'L':>2s} {'m':>3s} "+' '.join(f'{"base@"+str(k):>11s} {"EI@"+str(k):>11s}' for k in KS))
    for Lv in sorted(strata):
        ns=strata[Lv]; line=f'  {Lv:2d} {len(ns):3d} '
        for k in KS:
            bv=[passk(by[(st,'base',seed,0.8)][n],k) for n in ns]
            ev=[passk(by[(st,'ei',seed,0.8)][n],k) for n in ns]
            b=sum(x for x,_ in bv)/len(ns); e=sum(x for x,_ in ev)/len(ns)
            line+=f"{b:10.4f}{'*' if any(f for _,f in bv) else ' '} {e:10.4f}{'*' if any(f for _,f in ev) else ' '} "
        print(line)
    print()
    print('  crossover (smallest k in 1..10,000 where base pass@k >= EI pass@k, per stratum):')
    for Lv in sorted(strata):
        ns=strata[Lv]; cross=None
        for k in list(range(1,64))+[int(64*1.15**i) for i in range(1,60)]:
            if k>10000: break
            b=sum(passk(by[(st,'base',seed,0.8)][n],k)[0] for n in ns)/len(ns)
            e=sum(passk(by[(st,'ei',seed,0.8)][n],k)[0] for n in ns)/len(ns)
            if b>=e: cross=k; break
        print(f'    L{Lv:2d}: {"k="+str(cross) if cross else "none within measured k<=10,000"}')
    print()
