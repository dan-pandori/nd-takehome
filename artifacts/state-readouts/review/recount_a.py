# reviewer's own Part A recount: rows + dump cross-check
import json, gzip, glob, statistics, collections
D='artifacts/state-readouts/'
thm={}
for l in open('data/sc/theorems.jsonl'):
    r=json.loads(l); thm[r['name']]=r
names=[l.strip() for l in open('data/sc/falsifier_survivors.txt') if l.strip()]
assert len(names)==29 and len(set(names))==29
def prompt_of(n):
    r=thm[n]
    return r.get('prompt')
def rows(f):
    return {r['name']:r for r in map(json.loads,open(f))}
out={}
for arm in ['S','SH']:
  for s in [0,1]:
    a=rows(f'{D}H_{arm}_T08_s{s}.s0.jsonl'); b={}
    try: b=rows(f'{D}H_{arm}_T10_s{s}.s0.jsonl')
    except FileNotFoundError: pass
    t10names=[l.strip() for l in open(f'{D}H_T10_names_{arm}_s{s}.txt') if l.strip()]
    assert set(a)==set(names), (arm,s,set(names)-set(a))
    # dump: per prompt accepted?
    acc=collections.Counter(); ndist=collections.Counter()
    for T in ['T08','T10']:
        fn=f'{D}dump/H_{arm}_{T}_s{s}.jsonl.gz'
        for l in gzip.open(fn,'rt'):
            r=json.loads(l)
            if r['lean_ok']: acc[(T,r['prompt'])]+=1
    reached=[];reached_dump=[]; phat=[]; tried=0; cap=0; stepcap=0; truncact=0
    t10_needed=[n for n in names if a[n]['n_ok']<5]
    for n in names:
        ok=a[n]['n_ok']+(b[n]['n_ok'] if n in b else 0)
        if ok>0: reached.append(n)
        p=prompt_of(n)
        if acc[('T08',p)]+acc[('T10',p)]>0: reached_dump.append(n)
        phat.append(a[n]['n_ok']/a[n]['n_tried'])
        for rr in [a[n]]+([b[n]] if n in b else []):
            tried+=rr['n_tried']; stepcap+=rr['n_step_cap']; truncact+=rr['n_trunc_action']
        # row consistency: n_ok+parse+rej==tried
        for rr in [a[n]]+([b[n]] if n in b else []):
            if rr['n_ok']+rr['n_parse_fail']+rr['n_leanrej']!=rr['n_tried']: print('  row sum mismatch',arm,s,n,rr['stage'] if 'stage' in rr else '')
            if rr['n_ok']<5 and rr['n_tried']<rr['k_requested']: print('  short row (not stopped, <k):',arm,s,n,rr['temperature'],rr['n_tried'])
    miss_t10=[n for n in t10_needed if n not in b]
    print(f'{arm} s{s}: reached rows {len(reached)}/29, dump {len(reached_dump)}/29, T08-only {sum(1 for n in names if a[n]["n_ok"]>0)}',
          f'| T10 needed {len(t10_needed)} names-file {len(t10names)} done {len(b)} missing {len(miss_t10)}',
          f'| median p08 {statistics.median(phat):.4g} | tried {tried} stepcap {stepcap} ({stepcap/tried:.4%}) truncact {truncact} ({truncact/tried:.4%})')
    if set(reached)!=set(reached_dump): print('  DIFF rows vs dump', set(reached)^set(reached_dump))
    if miss_t10: print('  T10 not run:', miss_t10, 'T08 attempts', [a[n]['n_tried'] for n in miss_t10])
    out[f'{arm}_s{s}']={'reached':sorted(reached),'t10_missing':miss_t10,'phat08':{n:a[n]['n_ok']/a[n]['n_tried'] for n in names},
        'phat10':{n:b[n]['n_ok']/b[n]['n_tried'] for n in b}, 'tried':tried}
json.dump(out,open('rv/recount_a.json','w'),indent=1)
