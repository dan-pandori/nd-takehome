"""C3 recount: Q (gen L_true 13-16 /380), rr600 /600, textbook /73, per-bin, from literal-text Lean dumps."""
import sys, json, hashlib, collections
from common import *
pool = list(jl(ROOT + '/data/ladder/transfer_long_rr600.jsonl'))
byp = collections.defaultdict(list)
for r in pool: byp[r['prompt']].append(r)
dup = sum(1 for v in byp.values() if len(v) > 1)
Qset = {r['prompt'] for r in pool if r['source'] == 'gen' and 13 <= r['L_true'] <= 16}
print('pool', len(pool), 'distinct prompts', len(byp), 'dup prompts', dup, '|Q|', len(Qset),
      'textbook', sum(r['source'] == 'textbook' for r in pool))
SC = RAW + '/state-cap12/artifacts/sc12/dump/'
files = {
 'SN12_T1_s0': SC + 'rr_T1_SN12_s0__rr600.jsonl.gz', 'SN12_T1_s1': MY + '/rr_T1_SN12_s1__rr600.jsonl.gz',
 'SN12_T1_s2': MY + '/rr_T1_SN12_s2__rr600.jsonl.gz', 'SN12_T1_s3': MY + '/rr_T1_SN12_s3__rr600.jsonl.gz',
 'SN12_Fz_s0': SC + 'rr_stage1_SN12_s0__rr600.jsonl.gz', 'SN12_Fz_s1': MY + '/rr_stage1_SN12_s1__rr600.jsonl.gz',
 'SN12_Fz_s2': MY + '/rr_stage1_SN12_s2__rr600.jsonl.gz', 'SN12_Fz_s3': MY + '/rr_stage1_SN12_s3__rr600.jsonl.gz',
 'K12_T1_s0': SC + 'rr_T1_K12_s0__rr600.jsonl.gz', 'K12_T1_s1': MY + '/rr_T1_K12_s1__rr600.jsonl.gz'}
out = {}
for lab, fn in files.items():
    md5 = hashlib.md5(open(fn, 'rb').read()).hexdigest()
    acc = collections.defaultdict(list); n = 0; notpool = 0
    for d in jl(fn):
        n += 1
        if d['prompt'] not in byp: notpool += 1; continue
        if truthy(d['lean_ok']): acc[d['prompt']].append(d['lean_text'])
    S = set(acc)
    q = len(S & Qset)
    bins = collections.Counter(r['L_true'] for p in S for r in byp[p][:1] if r['source'] == 'gen')
    tb = sum(1 for p in S if byp[p][0]['source'] == 'textbook')
    out[lab] = dict(md5=md5, rows=n, notpool=notpool, solved600=len(S), Q=q, textbook=tb,
                    bins={b: bins[b] for b in range(11, 17)}, solved=sorted(S))
    print('%-11s md5 %s rows %6d notpool %d  rr600 %3d  Q %3d  tb %2d  gen-bins %s' % (lab, md5[:8], n, notpool, len(S), q, tb,
          ' '.join('%d:%d' % (b, bins[b]) for b in range(11, 17))))
json.dump(out, open(ROOT + '/rv/C3C4/c3_solved.json', 'w'))
