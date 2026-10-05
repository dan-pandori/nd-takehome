#!/usr/bin/env python3
"""Reviewer: threshold sensitivity (r8, draw x0) of the budget definitions at K = m x K_eval-set, m in {0.1, 0.3, 1, 3}."""
import json, os, sys, math
from scipy.stats import beta
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rv_load as L
B = json.load(open(f'{L.RV}/review_cd/out_bracket.json')); S = json.load(open(f'{L.RV}/review_cd/out_sets.json'))
SETS = json.load(open(f'{L.CD}/j1/sets.json'))
TC = json.load(open(os.path.expanduser('~/work/trajectory/artifacts/tj/compute.json')))
def cpl(c, n): return 0.0 if c == 0 else float(beta.ppf(0.05, c, n - c + 1))
for s in (0, 1, 2):
    K0 = TC[f'T1 ladder|{s}']['gpu_seconds'] / (322 * 3.6e-3)
    E = S['eqk'][f's{s}_r8_x0']; H = set(SETS[str(s)]['H']); b = B[str(s)]
    out = []
    for m in (0.1, 0.3, 1, 3):
        K = K0 * m; cm = und = tf = br = 0
        for n in E:
            c, N = b['ps'][n]
            cm += N >= K and c / N < 1 / K; und += N < K and c == 0
            if n in b['MX']: tf += b['MX'][n] < -math.log(K)
            if n in H:
                lb = b['LB'][n]['pend'][1] if n in b['LB'] else -math.inf
                br += not (lb >= math.log(2) - math.log(K) or cpl(c, N) >= 1 / K)
        out.append(f'K x{m} ({K:,.0f}): cm {cm} (undet {und}) tfmax {tf} brk_ne {br}')
    print(f's{s} (eqk {len(E)}): ' + ' | '.join(out))
