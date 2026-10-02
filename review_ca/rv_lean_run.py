import json,sys,os,random,collections
sys.path.insert(0,os.path.expanduser('~/review/claim-audit/rv')); from rv_lean import *
R=os.path.expanduser('~/review/claim-audit/audit/raw/')
ref=set(open(R+'support-curves/data/sc/falsifier_survivors.txt').read().split())
thm={json.loads(l)['name']:json.loads(l)['thm'] for l in open(R+'ca/surv.jsonl')}
arms={'R2 EI s0 (CA re-sample)':['ca/R2_EI_s0_T08.s0.jsonl'],'R1 SN base s0 (CA re-sample)':['ca/R1_SNbase_s0_T08.s0.jsonl'],
 'R3 WP base s1 (CA re-sample)':['ca/R3_base_s1_T08.s0.jsonl','ca/R3_base_s1_T08.s1.jsonl'],
 'SN base s0+s1 T0.8 (support-state)':['ss/H_base_T08_s0.s0.jsonl','ss/H_base_T08_s1.s0.jsonl'],
 'EI s0 T0.8 (support-curves)':['support-curves/artifacts/sc/s1_ei_T08_s0.s0.jsonl','support-curves/artifacts/sc/s1_ei_T08_s0.s1.jsonl']}
res={}; allp=[]
for arm,fs in arms.items():
    ok=0;n=0;rej=[];ts=[];stored=[];ln=[]
    for f in fs:
        for l in open(R+f):
            r=json.loads(l)
            if r['name'] not in ref: continue
            for p in r['proofs']:
                n+=1; a,why=check(thm[r['name']],p['lean_text'])
                ok+=a
                if not a: rej.append((r['name'],why))
                ts.append(term_size(p['lean_text'])); stored.append(p.get('term_size')); ln.append(nlines(p['lean_text']))
                allp.append((arm,r['name'],p['lean_text']))
    res[arm]=dict(n=n,lean_ok=ok,rejected=rej[:5],term_size_min_med_max=(min(ts),sorted(ts)[len(ts)//2],max(ts)),
                  haves_min_med_max=(min(ln),sorted(ln)[len(ln)//2],max(ln)),
                  corr_with_stored_term_size=None)
    print(arm,res[arm],flush=True)
# negative controls on a fixed random sample of 40 proofs
random.seed(7); smp=random.sample(allp,40); names=list(thm)
nc=collections.Counter(); ncrej=collections.Counter()
def drop_have(t):
    parts=t.split(' ; '); idx=[i for i,x in enumerate(parts) if x.startswith('have') and ':= h' not in x]
    if not idx: idx=[i for i,x in enumerate(parts) if x.startswith('have')]
    del parts[idx[len(idx)//2]]; return ' ; '.join(parts)
for arm,nm,t in smp:
    other=random.choice([x for x in names if thm[x]!=thm[nm]])
    ctrls={'drop_have':(thm[nm],drop_have(t)),'swap_h1_h2':(thm[nm],t.replace('h1','hX').replace('h2','h1').replace('hX','h2')) if 'h2' in t else (thm[nm],t.replace('h1','h2')),
           'other_theorem':(thm[other],t),'truncate_half':(thm[nm],t[:len(t)//2])}
    for k,(th,tt) in ctrls.items():
        if tt==t and th==thm[nm]: continue
        nc[k]+=1; a,_=check(th,tt); ncrej[k]+= (not a)
print('NEG CONTROLS', {k:f'{ncrej[k]}/{nc[k]} rejected' for k in nc})
json.dump(dict(res=res,neg={k:[ncrej[k],nc[k]] for k in nc}),open(os.path.expanduser('~/review/claim-audit/rv/rv_lean_out.json'),'w'),indent=1)
