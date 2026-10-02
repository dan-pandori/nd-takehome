# reviewer: R1/R2/R3 re-sample vs on-file, per-theorem two-proportion z (pooled), stop_at-aware note
import json,math,collections,os
R=os.path.expanduser('~/review/claim-audit/audit/raw/')
ref=set(open(R+'support-curves/data/sc/falsifier_survivors.txt').read().split())
def load(fs,filt=lambda r:True):
    d=collections.defaultdict(lambda:[0,0])
    for f in fs:
        for l in open(R+f):
            r=json.loads(l)
            if r['name'] in ref and filt(r): d[r['name']][0]+=r['n_ok']; d[r['name']][1]+=r['n_tried']
    return d
def z(a,b):
    (c1,n1),(c2,n2)=a,b; p=(c1+c2)/(n1+n2)
    if p in (0,1): return 0.0
    return (c1/n1-c2/n2)/math.sqrt(p*(1-p)*(1/n1+1/n2))
def cmp(name,new,old):
    zs={t:z(new[t],old[t]) for t in ref if t in new and t in old}
    bad={t:(new[t],old[t],round(v,2)) for t,v in zs.items() if abs(v)>2.6}
    sn=sum(new[t][0]>0 for t in new); so=sum(old[t][0]>0 for t in old)
    print(f'{name}: solved new {sn}/{len(new)} old {so}/{len(old)}; |z|>2.6: {len(bad)}', bad)
    print('  max|z|', max(abs(v) for v in zs.values()))
r1=load(['ca/R1_SNbase_s0_T08.s0.jsonl']); h0=load(['ss/H_base_T08_s0.s0.jsonl'])
cmp('R1 SN base s0 T0.8 vs support-state H',r1,h0)
print('  R1 n per theorem', sorted(set(v[1] for v in r1.values())))
print('  R1 unsolved', sorted(t for t in r1 if r1[t][0]==0), ' H unsolved', sorted(t for t in h0 if h0[t][0]==0))
r2=load(['ca/R2_EI_s0_T08.s0.jsonl']); e0=load(['support-curves/artifacts/sc/s1_ei_T08_s0.s0.jsonl','support-curves/artifacts/sc/s1_ei_T08_s0.s1.jsonl'])
cmp('R2 EI s0 T0.8 vs support-curves s1_ei',r2,e0)
print('  R2 p-hat range', min(v[0]/v[1] for v in r2.values()), max(v[0]/v[1] for v in r2.values()), 'min hits',min(v[0] for v in r2.values()))
r3=load(['ca/R3_base_s1_T08.s0.jsonl','ca/R3_base_s1_T08.s1.jsonl'])
prev=load(['support-curves/artifacts/sc/s3_base_T08_s1.s0.jsonl','support-curves/artifacts/sc/s3_base_T08_s1.s1.jsonl','support-followups/a_base_T08_s1.s0.jsonl'])
print('R3 base s1 solved', sorted((t,r3[t]) for t in r3 if r3[t][0]>0))
print('   prior base-s1 20k solved', sorted((t,prev[t]) for t in prev if prev[t][0]>0))
print('   union', len({t for t in r3 if r3[t][0]>0}|{t for t in prev if prev[t][0]>0}))
print('   R3 attempts on unsolved', sorted(set(r3[t][1] for t in r3 if r3[t][0]==0)))
