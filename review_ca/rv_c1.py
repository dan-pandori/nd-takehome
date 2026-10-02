# reviewer recount C1: survivors = base-s0 0 hits over all base-s0 stages, EI-s0 >=1 hit.
import json,glob,collections,os
D=os.path.expanduser('~/review/claim-audit/audit/raw/support-curves/artifacts/sc/')
agg=collections.defaultdict(lambda: collections.Counter())
for f in glob.glob(D+'s*_*.s*.jsonl'):
    for l in open(f):
        r=json.loads(l)
        key=(r['model'],r['ckpt_md5'][:6],r['temperature'])
        agg[r['name']][key+('n',)]+=r['n_tried']; agg[r['name']][key+('c',)]+=r['n_ok']
B0='9bde44'; B1='fc27e5'; E0='5cebd7'; E1='105be4'
def tot(c,md,what,T=None): return sum(v for k,v in c.items() if k[1]==md and k[3]==what and (T is None or k[2]==T))
surv=[t for t,c in agg.items() if tot(c,B0,'c')==0 and tot(c,E0,'c')>0]
print('theorems',len(agg),'survivors',len(surv))
ref=set(open(os.path.expanduser('~/review/claim-audit/audit/raw/support-curves/data/sc/falsifier_survivors.txt')).read().split())
print('== falsifier_survivors.txt',set(surv)==ref, len(ref-set(surv)), len(set(surv)-ref))
ns=[tot(agg[t],B0,'n') for t in surv]; print('base s0 attempts per survivor min/max',min(ns),max(ns))
print('base s0 T0.8 n min/max',min(tot(agg[t],B0,'n',0.8) for t in surv),max(tot(agg[t],B0,'n',0.8) for t in surv))
ps=sorted(tot(agg[t],E0,'c',0.8)/max(1,tot(agg[t],E0,'n',0.8)) for t in surv); print('EI s0 T0.8 p range',ps[0],ps[-1], 'zero at T0.8:',sum(p==0 for p in ps))
pall=sorted(tot(agg[t],E0,'c')/tot(agg[t],E0,'n') for t in surv); print('EI s0 all-T p range',pall[0],pall[-1])
print('base s1 (10k T0.8) hits on survivors', sum(tot(agg[t],B1,'c')>0 for t in surv), [t for t in surv if tot(agg[t],B1,'c')>0])
print('EI s1 hits on survivors', sum(tot(agg[t],E1,'c')>0 for t in surv))
json.dump(sorted(surv),open(os.path.expanduser('~/review/claim-audit/rv/rv_survivors.json'),'w'))
print('--- split by base attempts')
for t in sorted(surv,key=lambda t:-tot(agg[t],B0,'n')):
    pe=tot(agg[t],E0,'c',0.8)/tot(agg[t],E0,'n',0.8)
    print(t, tot(agg[t],B0,'n'), round(pe,5), t in ref)
