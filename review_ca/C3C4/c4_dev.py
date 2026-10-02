import hashlib, json, math
from common import *
T = list(jl(ROOT + '/data/ladder/transfer.jsonl'))
dev = [r for r in T if int(hashlib.sha1(r['key'].encode()).hexdigest(), 16) % 2 == 0]
P = {r['prompt'] for r in dev}
print('transfer', len(T), 'dev(sha1 even)', len(dev), 'distinct prompts', len(P), 'L_true>=7', sum(r['L_true'] >= 7 for r in dev))
res = {}
for lab in ['T1_SN6_s0', 'T1_SN6_s1', 'T1_SN12_s0', 'T1_SN12_s1', 'T1_SN12_s2', 'T1_SN12_s3', 'T1_best6_s0', 'T1_best6_s1', 'T1_best6_s2', 'T1_best12_s0', 'T1_best12_s1', 'T1_best12_s2']:
    rows = list(jl(MY + '/bs/%s__dev.jsonl' % lab))
    ps = {d['prompt'] for d in rows}
    S = {d['prompt'] for d in rows if truthy(d['solved']) and d.get('proofs')}
    res[lab] = len(S & P)
    print('%-13s rows %d  rows==dev %s  ktried %s  solved %d' % (lab, len(rows), ps == P, sorted({d['n_tried'] for d in rows}), len(S & P)))
def cell(pfx, ss): return [res[pfx % s] for s in ss]
for cap, o, b in (('6', cell('T1_SN6_s%d', (0, 1)), cell('T1_best6_s%d', range(3))), ('12', cell('T1_SN12_s%d', range(4)), cell('T1_best12_s%d', range(3)))):
    print('dev T1 cap', cap, 'ours', o, 'best', b, 'mean diff %+.1f' % (sum(b)/len(b) - sum(o)/len(o)), 'sep', min(b) > max(o))
