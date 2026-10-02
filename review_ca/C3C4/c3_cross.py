import json, math, collections, hashlib
from common import *
pool = {r['prompt']: r for r in jl(ROOT + '/data/ladder/transfer_long_rr600.jsonl')}
Q = {p for p, r in pool.items() if r['source'] == 'gen' and 13 <= r['L_true'] <= 16}
base = json.load(open(ROOT + '/rv/C3C4/c3_solved.json'))
def from_rr(fn):
    S = set(); n = 0; miss = 0
    for d in jl(fn):
        n += 1
        if d['prompt'] not in pool: miss += 1; continue
        if truthy(d['solved']): S.add(d['prompt'])
    return S, n, miss
def from_dump(fn):
    return {d['prompt'] for d in jl(fn) if truthy(d['lean_ok']) and d['prompt'] in pool}, None, 0
def z(a, b, n=380):
    p1, p2 = a/n, b/n; p = (a+b)/(2*n); se = math.sqrt(2*p*(1-p)/n) if 0 < p < 1 else 1
    return (p1-p2)/se
L2 = RAW + '/long-pool-2/artifacts/lpool2/rr/'
pairs = [
 ('SN12_T1_s0', 'state-cap12 ms96 dump', MY + '/rr_T1_SN12_s0__rr600_ms96.jsonl.gz', from_dump),
 ('SN12_T1_s1', 'state-cap12 ms96 dump', MY + '/rr_T1_SN12_s1__rr600_ms96.jsonl.gz', from_dump),
 ('SN12_T1_s2', 'long-pool-2 ms96 rr', L2 + 'T1_SN12_s2_ms96__rr600.jsonl', from_rr),
 ('SN12_T1_s3', 'long-pool-2 ms96 rr', L2 + 'T1_SN12_s3_ms96__rr600.jsonl', from_rr),
 ('K12_T1_s0', 'state-cap12 rr solved field', RAW + '/state-cap12/artifacts/sc12/rr/T1_K12_s0__rr600.jsonl', from_rr),
]
print('%-11s %-28s %4s %4s %6s | Q_a Q_b z  | Jaccard(Q-solved)' % ('ckpt', 'second read', 'rrA', 'rrB', 'miss'))
for lab, what, fn, f in pairs:
    A = set(base[lab]['solved']); B, n, miss = f(fn)
    qa, qb = len(A & Q), len(B & Q)
    jac = len(A & B & Q) / max(1, len((A | B) & Q))
    print('%-11s %-28s %4d %4d %6s | %3d %3d %+.2f | %.3f  onlyA %d onlyB %d' % (lab, what, len(A), len(B), miss, qa, qb, z(qa, qb), jac, len((A-B)&Q), len((B-A)&Q)))
# long-pool rr vs rr2 (two passes, inherited comparators)
LP = RAW + '/long-pool/artifacts/lpool/'
for nm in ['state-env__la_T1_SN_s0_r8', 'state-env__la_T1_SN_s1_r8', 'state-env__stage1_SN_s0', 'state-env__stage1_SN_s1', 'cap-horizon__stage1_k12_s0', 'ds-generator__la_T1_c0_s0_r8', 'ds-generator__la_T1_c0_s1_r8']:
    r = []
    for ps in ('rr', 'rr2'):
        S, n, miss = from_rr(LP + ps + '/' + nm + '.jsonl'); r.append((S, n, miss))
    (A, na, ma), (B, nb, mb) = r
    print('%-30s rr n=%d miss=%d Q=%d | rr2 n=%d miss=%d Q=%d | z %+.2f' % (nm, na, ma, len(A & Q), nb, mb, len(B & Q), z(len(A & Q), len(B & Q))))
