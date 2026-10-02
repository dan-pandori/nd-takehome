import json, math
from common import *
TB = {r['prompt'] for f in ('textbook_dev', 'textbook_train') for r in jl(ROOT + '/data/eval_only/textbook72/%s.jsonl' % f)}
def es(fn): return {d['prompt'] for d in jl(fn) if truthy(d['solved']) and d.get('proofs') and d['prompt'] in TB}
def z(a, b, n=72):
    p = (a + b) / (2 * n); return 0 if p in (0, 1) else (a - b) / n / math.sqrt(2 * p * (1 - p) / n)
base = json.load(open(ROOT + '/rv/C3C4/c4_tb72_solved.json'))
print('-- same checkpoint, two reads --')
pairs = [('T1_best12_s1 (bs) vs bs 2x caps', set(base['T1_best12_s1']), es(MY + '/bs/T1_best12_s1__tb72_cap.jsonl')),
         ('T1_SN12_s0 (tb72) vs tb72 diag a1024', set(base['T1_SN12_s0']), es(RAW + '/textbook72/artifacts/textbook72/diag/T1_SN12_s0_a1024.jsonl'))]
for run, d in (('tj', 'trajectory best12'), ('tj6', 'trajectory-cap6 best6')):
    for s in range(3):
        for c in ('pend', 'r8'):
            pairs.append(('%s s%d %s x0 vs x1' % (d, s, c), es(MY + '/%s/s%d_%s__tb72_x0.jsonl' % (run, s, c)), es(MY + '/%s/s%d_%s__tb72_x1.jsonl' % (run, s, c))))
for lab, A, B in pairs:
    print('%-40s %2d %2d z %+.2f onlyA %d onlyB %d' % (lab, len(A), len(B), z(len(A), len(B)), len(A - B), len(B - A)))
print('-- same recipe, different seeds/runs (not same ckpt) --')
for run, lab, bsk in (('tj', 'best12', 'best12'), ('tj6', 'best6', 'best6')):
    tr0 = [len(es(MY + '/%s/s%d_pend__tb72_x0.jsonl' % (run, s))) for s in range(3)]
    tr8 = [len(es(MY + '/%s/s%d_r8__tb72_x0.jsonl' % (run, s))) for s in range(3)]
    bF = [len(base['Fz_%s_s%d' % (bsk, s)]) for s in range(3)]; bT = [len(base['T1_%s_s%d' % (bsk, s)]) for s in range(3)]
    print('%s  trajectory r0 %s r8 %s | best-state Fz %s T1 %s | z(mean r8 vs mean T1) %+.2f' % (lab, tr0, tr8, bF, bT, z(sum(tr8)/3, sum(bT)/3)))
