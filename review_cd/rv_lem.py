#!/usr/bin/env python3
"""Reviewer: excluded-middle elicitation (Q10, Q11, J4, J6, J6b).  pass@256 of an instance = 1 if >= 1 of 256 attempts
is Lean-accepted (n = k, so the unbiased estimator is the indicator); 'held-out pass@256' = mean over instances.
lem40 = data/cd/j4/lem_transfer40.jsonl; lem39 = minus la_transfer_882 (its right disjunct is intuitionistic)."""
import json, os, sys, glob, collections
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rv_load as L
CD = L.CD
L40 = [r['name'] for r in L.rows(f'{L.RV}/data/cd/j4/lem_transfer40.jsonl')]
L39 = [n for n in L40 if n != 'la_transfer_882']
def rd(p):
    return {r['name']: (r['n_ok'], r['n_tried']) for r in L.rows(p)} if os.path.exists(p) else None
def summ(d, names):
    if d is None: return None
    sv = [d[n][0] > 0 for n in names]; p1 = [d[n][0] / d[n][1] for n in names]
    return np.mean(sv), np.mean(p1), sum(sv), len(names), {d[n][1] for n in names}
# h250 A v ~A instances (premise-free, conclusion X v ~X)
def is_lem(prompt):
    body = prompt.split('THM', 1)[1].rsplit('PRF', 1)[0]
    prem, concl = body.split(' SEQ ')
    if prem.strip(): return False
    t = concl.split()
    # strip outer parens and split at top-level 'v'
    if t[0] != '(' or t[-1] != ')': return False
    t = t[1:-1]; d = 0
    for i, x in enumerate(t):
        d += (x == '(') - (x == ')')
        if x == 'v' and d == 0:
            a, b = t[:i], t[i + 1:]
            return b == ['(', '~'] + a + [')'] or b == ['(', '~', '('] + a + [')', ')'] or (len(a) == 1 and b == ['(', '~', a[0], ')'])
    return False
PR = L.prompts()
H250 = L.pool_names('h250')
hl = [n for n in H250 if is_lem(PR[n])]
print('holdout250 premise-free A v ~A instances:', len(hl), hl)
print('\nJ4 (39 classical lem / 40):  solved@256 share, mean pass@1')
J4 = {}
for s in (0, 1, 2):
    for arm in ('pend', 'r16', 'A0', 'A4', 'A16', 'C16'):
        d = rd(f'{CD}/j4/s{s}_{arm}__lem40_x1.jsonl')
        a, b = summ(d, L39), summ(d, L40)
        J4[(s, arm)] = a
        print(f'  s{s} {arm:5s}: lem39 {a[2]:2d}/39 = {a[0]:.3f} (pass@1 {a[1]:.3f}); lem40 {b[2]}/40; k {a[4]}')
for s in (0, 1, 2):
    a0, a16 = rd(f'{CD}/j4/s{s}_A0__h250_x1.jsonl'), rd(f'{CD}/j4/s{s}_A16__h250_x1.jsonl')
    na0 = sum(v[0] > 0 for v in a0.values()); na16 = sum(v[0] > 0 for v in a16.values())
    print(f'  s{s} holdout250 solved@64: A0 {na0}  A16 {na16}  rel diff {(na16 - na0) / na0:+.3f}; k {set(v[1] for v in a0.values())}; '
          f'h250 lem instances solved: A0 {sum(a0[n][0] > 0 for n in hl)}/{len(hl)} A16 {sum(a16[n][0] > 0 for n in hl)}/{len(hl)}')
print('\nQ10 on h250 A v ~A instances (k 256 reads):')
for s in (0, 1, 2):
    for ck, x in (('pend', 0), ('pend', 1), ('r8', 0), ('r8', 1), ('r12', 1), ('r16', 1), ('r16', 0)):
        d = L.both(12, s, ck, x)
        print(f'  s{s} {ck:4s} x{x}: {sum(d[n][0] > 0 for n in hl)}/{len(hl)} solved; mean pass@1 {np.mean([d[n][0] / 256 for n in hl]):.3f}')
print('\nJ6 (no-DN knockout):')
for s in (0, 1, 2):
    g = json.load(open(f'{CD}/j6/s{s}_nodn__heldout_k1.json'))
    gp = json.load(open(os.path.expanduser(f'~/work/trajectory/artifacts/tj/eval/heldout_best12_s{s}_b1200.json')))
    nd = rd(f'{CD}/j6/s{s}_nodn__holdout250_k256.jsonl'); px1 = L.read(12, s, 'pend', 'h250', 1)
    l40 = rd(f'{CD}/j6/s{s}_nodn__lem_transfer40_k256.jsonl')
    a0 = rd(f'{CD}/j6/s{s}_nodn_A0__lem_transfer40_k256.jsonl'); a16 = rd(f'{CD}/j6/s{s}_nodn_A16__lem_transfer40_k256.jsonl')
    h64 = rd(f'{CD}/j6/s{s}_nodn_A16__holdout250_k64.jsonl')
    ndh = sum(v[0] > 0 for v in nd.values()); pdh = sum(v[0] > 0 for v in px1.values())
    print(f'  s{s}: held-out greedy nodn {g.get("rate")} vs pend {gp.get("rate")} (diff {gp.get("rate") - g.get("rate"):.3f}); '
          f'nodn h250@256 {ndh} vs pend x1 {pdh} ratio {ndh / pdh:.3f}; nodn lem40 solved {sum(v[0] > 0 for v in l40.values())}/40; '
          f'nodn+A0 lem39 {summ(a0, L39)[2]}/39; nodn+A16 lem39 {summ(a16, L39)[2]}/39 = {summ(a16, L39)[0]:.3f}; '
          f'|pend+A16 - nodn+A16| = {abs(J4[(s, "A16")][0] - summ(a16, L39)[0]):.3f}; nodn+A16 h250@64 {sum(v[0] > 0 for v in h64.values())}')
print('\nJ6b (replay from the knockout corpus; gain = A16n - C16n, mean over fine-tune seeds, lem39 solved@256 share):')
for s in (0, 1, 2):
    g = {}
    for m in ('pend', 'nodn'):
        v = {}
        for arm in ('A16n', 'C16n'):
            v[arm] = [summ(rd(f'{CD}/j6b/s{s}_{m}_{arm}_f{f}__lem40_x1.jsonl'), L39)[0] for f in (0, 1)]
        g[m] = np.mean(v['A16n']) - np.mean(v['C16n'])
        print(f'  s{s} {m}: A16n {v["A16n"]}  C16n {v["C16n"]}  gain {g[m]:.3f}')
    print(f'  s{s}: pend gain - knockout gain = {g["pend"] - g["nodn"]:+.3f}')
