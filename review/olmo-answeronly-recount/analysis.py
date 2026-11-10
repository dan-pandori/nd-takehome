import json,gzip,collections,csv,os,random,base64,sys
import numpy as np
B=os.path.expanduser('~/review/olmo-answeronly'); A=B+'/artifacts/olmo_answeronly/'
P={r['pid']:r for r in csv.DictReader(open(B+'/olmo_transplant/prompts.csv'))}
REACH=sorted([p for p in P if P[p]['set']=='reach']); CAL=sorted([p for p in P if P[p]['set']!='reach'])
def norm(t): return ' '.join(t.split())
# trace drafts: stored answer after think_k
from tokenizers import Tokenizer
tok=Tokenizer.from_file(os.path.expanduser('~/review/otr_rv/tok/allenai_Olmo-3-32B-Think-DPO/tokenizer.json'))
src={}
for f in ("F_s2300_ifb","C1_s2300_ifb","C2_s2300_ifb","Leval_main"):
    for l in gzip.open(f"{A}/inputs/{f}.jsonl.gz","rt"):
        r=json.loads(l); src[(r["job"],r["pid"],str(r["chunk"]),str(r["i"]))]=r
draft={}
def u(s): return np.frombuffer(base64.b64decode(s),dtype=np.int32).tolist()
for row in csv.DictReader(open(B+'/olmo_transplant/traces.csv')):
    if row['kind']!='rl': continue
    ids=u(src[(row['job'],row['pid'],row['chunk'],row['i'])]['ids'])
    draft[row['trace']]=norm(tok.decode(ids[int(row['think_k']):],skip_special_tokens=True))
for row in csv.DictReader(open(B+'/olmo_answeronly/lora_traces.csv')):
    ids=u(src[tuple(row['src'].split('|'))]['ids'])
    draft[row['trace']]=norm(tok.decode(ids[int(row['think_k']):],skip_special_tokens=True))
rows=[]
for j in ['R_dpo','R_s2300','C_dpo','C_s2300','L1_lora','L2_dpo','L3_lora','tp_R_dpo','tp_R_s2300','tp_C_dpo','tp_C_s2300']:
    sf=A+(f'inputs/{j}.jsonl.gz' if j.startswith('tp') else f'samples/{j}.jsonl.gz')
    g={(r['rid'],r['i']):r for r in map(json.loads,open(B+f'/rv/g_{j}.jsonl'))}
    for l in gzip.open(sf,'rt'):
        r=json.loads(l)
        if r['cond'] not in ('A1','A2','A3','A4','T1','T2','L1','L2','L3'): continue
        gr=g[(r['rid'],int(r['i']))]
        ans=norm(r['text'].rsplit('</think>',1)[-1])
        d=draft[r['trace']]
        def jac(a,b):
            A3={tuple(a.split()[i:i+3]) for i in range(max(1,len(a.split())-2))}; B3={tuple(b.split()[i:i+3]) for i in range(max(1,len(b.split())-2))}
            return len(A3&B3)/max(1,len(A3|B3))
        exact=ans==d; near=(not exact) and jac(ans,d)>=0.8
        stop=None
        if r['cond']=='A4': stop='exact' if exact else ('continues' if ans.startswith(d) else 'diverges')
        rows.append(dict(pid=r['pid'],set=P[r['pid']]['set'],w=r['writer'],c=r['cond'],strict=gr['strict'],ans=ans,
                         reopened=gr['reopened'],cut=r['finish']=='length',exact=exact,near=near,stop=stop,
                         n_tok=int(r['n_tok']),rid=r['rid'],i=int(r['i']),job=r['job'],trace=r['trace'],words=len(ans.split())))
json.dump(rows,open(B+'/rv/rows.json','w'))
print(len(rows))
