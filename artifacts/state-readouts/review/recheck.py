import json, gzip, glob, random, sys, collections
sys.path.insert(0,'rv'); from leancheck import check
from concurrent.futures import ThreadPoolExecutor
random.seed(20260930)
D='artifacts/state-readouts/dump/'
jobs=[]
for f in sorted(glob.glob(D+'*.jsonl.gz')):
    tag=f.split('/')[-1][:-9]
    acc=[];rej=[];filt=[]
    for l in gzip.open(f,'rt'):
        r=json.loads(l)
        it=(r['prompt'],r['lean_text'])
        if r['lean_ok']: acc.append(it)
        elif r['lean'] is False: rej.append(it)
        else: filt.append(it)
    nA=len(acc) if tag.startswith('H') else 150
    jobs.append((tag,'acc',random.sample(acc,min(nA,len(acc))),len(acc)))
    jobs.append((tag,'leanrej',random.sample(rej,min(60,len(rej))),len(rej)))
    jobs.append((tag,'filtrej',random.sample(filt,min(150 if tag.startswith('H') else 60,len(filt))),len(filt)))
cp=json.load(open('rv/classical_peirce.json'))
jobs.append(('classical_only_peirce_T1','acc',[(p,t) for _,_,p,t in cp],len(cp)))
def run(j):
    tag,kind,items,tot=j
    r=check(items) if items else []
    bad=[it for it,ok in zip(items,r) if ok!=(kind=='acc')]
    return {'tag':tag,'kind':kind,'n_checked':len(items),'n_total':tot,'n_lean_accept':sum(r),'mismatch':bad,'n_mismatch':len(bad)}
with ThreadPoolExecutor(2) as ex:
    out=list(ex.map(run,jobs))
for o in out: print(o['tag'],o['kind'],o['n_checked'],'/',o['n_total'],'accepted',o['n_lean_accept'],'MISMATCH' if o['n_mismatch'] else '',o['n_mismatch'] or '',flush=True)
json.dump(out,open('rv/recheck.json','w'),indent=1,ensure_ascii=False)
