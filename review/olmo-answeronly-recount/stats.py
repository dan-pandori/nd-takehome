import json,collections,random,os,sys,csv
import numpy as np
B=os.path.expanduser('~/review/olmo-answeronly')
rows=json.load(open(B+'/rv/rows.json'))
P={r['pid']:r for r in csv.DictReader(open(B+'/olmo_transplant/prompts.csv'))}
REACH=sorted(p for p in P if P[p]['set']=='reach'); CAL=sorted(p for p in P if P[p]['set']!='reach')
cell=collections.defaultdict(list)
for r in rows: cell[(r['w'],r['c'])].append(r)
GEN=None  # filled by caller: function(row)->genuine prob for strict rows
def rate(w,c,pids,kind='strict',reopen_fail=False):
    by=collections.defaultdict(list)
    for r in cell[(w,c)]:
        if r['pid'] in pids:
            v=r['strict'] and not (reopen_fail and r['reopened'])
            if kind=='genuine' and v: v=GEN(r)
            by[r['pid']].append(float(v))
    return {p:np.mean(by[p]) for p in pids if p in by}
def boot(f,pids,n=10000,seed=1):
    rng=np.random.default_rng(seed); pids=list(pids); out=[]
    for _ in range(n):
        s=[pids[i] for i in rng.integers(0,len(pids),len(pids))]; out.append(f(s))
    return np.percentile(out,[2.5,97.5])
def mean(d,ps): return float(np.mean([d[p] for p in ps if p in d]))
if __name__=='__main__':
    for st,ps in (('reach',REACH),('calib',CAL)):
        for w,c in sorted(cell):
            d=rate(w,c,ps)
            if not d: continue
            rs=cell[(w,c)]; rs=[r for r in rs if r['set']==st]
            n=len(rs)
            print(st,w,c,'strict %.3f'%mean(d,ps),'reopenfail %.3f'%mean(rate(w,c,ps,reopen_fail=True),ps),
                  'exact %.3f near %.3f'%(np.mean([r['exact'] for r in rs]),np.mean([r['near'] for r in rs])),
                  'cut %d/%d'%(sum(r['cut'] for r in rs),n),'reopen %d'%sum(r['reopened'] for r in rs),
                  'median words %d'%np.median([r['words'] for r in rs]),
                  ('stop '+str(collections.Counter(r['stop'] for r in rs)) if c=='A4' else ''))
    # strict-level R per cond (S_c on strict s2300 as a diagnostic)
    for c,ct in (('A1','A1'),('A2','A2'),('A3','A3'),('A4','A4'),('T1','T2')):
        s=rate('s2300',ct,REACH); S=[p for p in REACH if s[p]>=0.75]; d=rate('dpo',c,REACH)
        print('strict R',c,len(S),'%.3f'%(mean(d,S)/mean(s,S)), 'n s2300<0.75:',41-len(S))
