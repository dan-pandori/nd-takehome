#!/usr/bin/env python3
"""claim-audit re-sampling read-out (lead auditor's own code).
R1: SN base s0 (stage1_SN_s0.pt, ec3888d9; 3,216,384 params, lean_staten, from scratch on train_depth3_f0_a1) on the 29
    survivors, T 0.8, k 10,000, no early stop, seed 9001  vs  support-state H_base_T08_s0 (seed 1, stop_at 5).
R2: support-curves EI s0 (la_T1_sc_s0_r8.pt, 5cebd7ec; 3,214,336 params, lean_seq, base s0 + 8 EI rounds) on the 29,
    T 0.8, k 2,000, no early stop, seed 9002  vs  support-curves s1_ei_T08_s0 (the selection sample)."""
import json, glob, math, sys
def rows(pat):
    out = {}
    for f in sorted(glob.glob(pat)):
        for l in open(f):
            r = json.loads(l); out[r['name']] = (r['n_ok'], r['n_tried'])
    return out
def z(a, b):
    (k1, n1), (k2, n2) = a, b
    p = (k1 + k2) / (n1 + n2)
    if p in (0, 1): return 0.0
    return (k1 / n1 - k2 / n2) / math.sqrt(p * (1 - p) * (1 / n1 + 1 / n2))
S = open('/tmp/ca_surv.txt').read().split()
for tag, new, old in [('R2 EI s0', 'raw/ca/R2_EI_s0_T08.s0.jsonl', 'raw/support-curves/artifacts/sc/s1_ei_T08_s0.s*.jsonl'),
                      ('R1 SN base s0', 'raw/ca/R1_SNbase_s0_T08.s0.jsonl', 'raw/ss/H_base_T08_s0.s0.jsonl')]:
    A, B = rows(new), rows(old)
    common = [s for s in S if s in A and s in B]
    if not common: print(tag, 'no rows yet'); continue
    zs = [z(A[s], B[s]) for s in common]
    pa = sorted(A[s][0] / A[s][1] for s in common)
    print(f'{tag}: {len(common)} theorems | new reached {sum(A[s][0]>0 for s in common)} | old reached {sum(B[s][0]>0 for s in common)}'
          f' | new p>=0.01 {sum(A[s][0]/A[s][1]>=0.01 for s in common)} | old p>=0.01 {sum(B[s][0]/B[s][1]>=0.01 for s in common)}'
          f' | new min p {pa[0]:.4f} median {pa[len(pa)//2]:.4f} | |z|>2: {sum(abs(x)>2 for x in zs)} |z|>3: {sum(abs(x)>3 for x in zs)}')
    for s in common:
        if abs(z(A[s], B[s])) > 2 or (A[s][0] > 0) != (B[s][0] > 0):
            print(f'   {s}: new {A[s][0]}/{A[s][1]}  old {B[s][0]}/{B[s][1]}  z {z(A[s], B[s]):+.1f}')
