import json,gzip,collections,csv,random,os,hashlib
B=os.path.expanduser('~/review/olmo-answeronly'); A=B+'/artifacts/olmo_answeronly/'
P={r['pid']:r for r in csv.DictReader(open(B+'/olmo_transplant/prompts.csv'))}
probs={json.loads(l)['pid']:json.loads(l) for l in open(B+'/olmo_ifomega/problems.jsonl') if '"ifbench_' in l}
rng=random.Random(4242)
succ=collections.defaultdict(list)
def load(sf,gf,jobfilter=None):
    g={(r['rid'],r['i']):r for r in map(json.loads,open(gf))}
    for l in gzip.open(sf,'rt'):
        r=json.loads(l); gr=g[(r['rid'],int(r['i']))]
        if P[r['pid']]['set']!='reach' or not gr['strict']: continue
        if jobfilter and r['cond'] not in jobfilter: continue
        ans=r['text'].rsplit('</think>',1)[-1].strip()
        succ[(r['writer'],r['cond'])].append((r['pid'],ans,r['rid'],int(r['i'])))
for j in ['R_dpo','R_s2300','L1_lora','L2_dpo']: load(A+f'samples/{j}.jsonl.gz',f'rv/g_{j}.jsonl')
load(A+'inputs/tp_R_dpo.jsonl.gz','rv/g_tp_R_dpo.jsonl',{'T1'})
plan={('dpo','A1'):None,('dpo','T1'):None,('dpo','A2'):80,('dpo','A3'):80,('dpo','A4'):80,('s2300','A1'):80,('lora_main','L1'):60,('dpo','L2'):60}
items={}; sel=[]
for cell,k in plan.items():
    rows=succ[cell]; pick=rows if k is None else rng.sample(rows,min(k,len(rows)))
    for pid,ans,rid,i in pick:
        key=(pid,' '.join(ans.split()))
        if key not in items: items[key]=(pid,ans)
        sel.append({'cell':'|'.join(cell),'pid':pid,'rid':rid,'i':i,'text_key':hashlib.sha1(json.dumps(key).encode()).hexdigest()})
keys=list(items); rng.shuffle(keys); kmap={}
for n,key in enumerate(keys):
    iid='x'+hashlib.sha1(f'rv{n}{key}'.encode()).hexdigest()[:7]
    pid,ans=items[key]; p=probs[pid]
    cons='\n'.join(f'- {cid} {json.dumps({a:b for a,b in kw.items() if b is not None})} -> checker: followed' for cid,kw in zip(p['instruction_id_list'],p['kwargs']))
    open(f'rv/hand/items/{iid}.md','w').write(f'# item {iid}\n\n## Prompt\n\n{p["prompt"]}\n\n## Constraints\n\n{cons}\n\n## Answer\n\n{ans}\n')
    kmap[hashlib.sha1(json.dumps(key).encode()).hexdigest()]=iid
for s in sel: s['item']=kmap[s['text_key']]
os.makedirs('rv/hand_key',exist_ok=True)
json.dump(sel,open('rv/hand_key/selection.json','w'))
print(len(items),'distinct items',collections.Counter(s['cell'] for s in sel))
ids=sorted(set(kmap.values())); rng.shuffle(ids)
bs=[ids[i:i+40] for i in range(0,len(ids),40)]
json.dump(bs,open('rv/hand/batches.json','w')); print(len(bs),'batches')
