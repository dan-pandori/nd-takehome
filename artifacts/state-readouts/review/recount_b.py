import json, gzip, collections, glob
D='artifacts/state-readouts/'
DEAD=['demorgan_and_to_nor','demorgan_nor_to_and','demorgan_or_to_nand','dist_and_over_or','dist_and_over_or_conv',
'dist_or_over_and','excluded_middle','import','negated_conditional','negated_conditional_conv','peirce','peirce_sequent']
pools={'tb':'data/sr/textbook_transfer.jsonl','tbl':'data/sr/textbook_long.jsonl'}
P={k:[json.loads(l) for l in open(v)] for k,v in pools.items()}
for k,v in P.items():
    c=collections.Counter(r['schema'] for r in v); print(k,len(v),len(c),dict(c)); assert all(r['source']=='textbook' for r in v)
# check pools equal to the ladder transfer textbook subsets
import subprocess
out={}
for arm in ['T1','Fz']:
  for s in range(4):
    for pk in ['tb','tbl']:
        pool={r['prompt']:r for r in P[pk]}
        ok=collections.Counter()
        for l in gzip.open(f'{D}dump/rr_{arm}_s{s}__{pk}.jsonl.gz','rt'):
            r=json.loads(l)
            assert r['prompt'] in pool
            if r['lean_ok']: ok[r['prompt']]+=1
        rows={r['name']:r for r in map(json.loads,open(f'{D}rr/{arm}_s{s}__{pk}.jsonl'))}
        solved_rows={n for n,r in rows.items() if r['solved']}
        solved_dump={pool[p]['name'] for p in ok}
        by=collections.Counter(pool[p]['schema'] for p in ok)
        summ=json.load(open(f'{D}rr/{arm}_s{s}__{pk}.json'))
        tr=summ['env']['env_end'].get('truncated',0); ns=summ['n_samples']
        stepmax=max(int(x) for x in summ['env']['env_steps'])
        line=f'{arm} s{s} {pk}: solved dump {len(solved_dump)} rows {len(solved_rows)} summ {summ["solved"]}/{summ["n"]}; trunc {tr}/{ns}={tr/ns:.3%} maxsteps {stepmax}'
        if pk=='tb':
            d5=[d for d in DEAD if by[d]>=5]
            line+=f' | dead>=5: {len(d5)} ; EM {by["excluded_middle"]}; dead: '+' '.join(f'{d[:10]}={by[d]}' for d in DEAD)
        else:
            line+=' | '+' '.join(f'{k}={v}' for k,v in sorted(by.items()))
        if solved_dump!=solved_rows: line+=f' DIFF {len(solved_dump^solved_rows)}'
        print(line)
        out[f'{arm}_s{s}_{pk}']={'solved':len(solved_dump),'by_schema':dict(by)}
json.dump(out,open('rv/recount_b.json','w'),indent=1)
