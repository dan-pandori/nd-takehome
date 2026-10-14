"""review_coep/descr.py -- addendum-5 descriptives and the exact tests, with an own one-sided Boschloo test (groups are
the ROWS here: x1 of n1 in arm 1 vs x2 of n2 in arm 2; scipy's boschloo_exact treats columns as groups, see
reviewer-recount-traps).  Inputs: review_coe/out_acq.json (create-or-elicit reviewer's per-read strict counts)."""
import json, os, sys, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *


def comb(n, k):
    return math.comb(n, k)


def fisher_upper(a, n1, b, n2):
    """one-sided Fisher p for arm 1 > arm 2: P(A >= a | margins)"""
    m = a + b
    tot = comb(n1 + n2, m)
    return sum(comb(n1, x) * comb(n2, m - x) for x in range(a, min(n1, m) + 1)) / tot


def boschloo(x1, n1, x2, n2, grid=20001):
    obs = fisher_upper(x1, n1, x2, n2)
    tabs = [(a, b) for a in range(n1 + 1) for b in range(n2 + 1) if fisher_upper(a, n1, b, n2) <= obs + 1e-12]
    best = 0.0
    for i in range(grid):
        p = i / (grid - 1)
        s = sum(comb(n1, a) * p ** a * (1 - p) ** (n1 - a) * comb(n2, b) * p ** b * (1 - p) ** (n2 - b) for a, b in tabs)
        best = max(best, s)
    return best


print('self-test: 6/6 vs 0/6', round(boschloo(6, 6, 0, 6), 6), '(2^-12 =', round(2 ** -12, 6), '); 5/6 vs 0/6',
      round(boschloo(5, 6, 0, 6), 5), '; 1/6 vs 0/6', round(boschloo(1, 6, 0, 6), 4))
acq = json.load(open(P('review_coe/out_acq.json')))['reads']
FAM = families()


def bar_fams(tag):
    return set(acq[tag]['strict']['acquired'])


print('\n== families at the bar (plain x0): pend -> r16; acquired during RL = at the bar at r16, not at pend')
rl = {}
for arm, seeds in (('full', range(6)), ('ko', range(6)), ('dose1', range(3))):
    for s in seeds:
        t = f'{arm}_s{s}'
        p0, p16 = bar_fams(f'pend_{t}_x0'), bar_fams(f'r16_{t}_x0')
        rl[t] = sorted(p16 - p0)
        print(f'  {t:9s} pend {sorted(p0)}  r16 {sorted(p16)}  RL-acquired {rl[t]}')
nf = sum(1 for s in range(6) if rl[f'full_s{s}']); nk = sum(1 for s in range(6) if rl[f'ko_s{s}'])
nfn = sum(1 for s in (3, 4, 5) if rl[f'full_s{s}'])
print(f'  RL-acquired seeds: full {nf}/6, knockout {nk}/6 -> Boschloo one-sided p = {boschloo(nf, 6, nk, 6):.5f}')
print(f'  hardware-matched (new full seeds s3-s5 on A40, like the knockout): {nfn}/3 vs {nk}/6 -> p = {boschloo(nfn, 3, nk, 6):.4f}')
anyf = sum(1 for s in range(6) if bar_fams(f'r16_full_s{s}_x0')); anyk = sum(1 for s in range(6) if bar_fams(f'r16_ko_s{s}_x0'))
anyfn = sum(1 for s in (3, 4, 5) if bar_fams(f'r16_full_s{s}_x0'))
print(f'  >= 1 family at the bar at r16: full {anyf}/6, knockout {anyk}/6 -> p = {boschloo(anyf, 6, anyk, 6):.6f}; '
      f'new full seeds only {anyfn}/3 vs {anyk}/6 -> p = {boschloo(anyfn, 3, anyk, 6):.4f}')
print('\n== strict members solved, plain x0 / x1 / guided g0, pend and r16, and RL-phase gains')
for arm, seeds in (('full', range(6)), ('ko', range(6)), ('dose1', range(3))):
    for s in seeds:
        t = f'{arm}_s{s}'
        g = lambda k: acq[k]['strict']['solved'] if k in acq else None
        v = {k: g(f'{k.split("_")[0]}_{t}_{k.split("_")[1]}') for k in ('pend_x0', 'pend_x1', 'pend_g0', 'r16_x0', 'r16_x1', 'r16_g0')}
        gain = {x: (v[f'r16_{x}'] - v[f'pend_{x}']) if v[f'r16_{x}'] is not None and v[f'pend_{x}'] is not None else None
                for x in ('x0', 'x1', 'g0')}
        print(f'  {t:9s} {v}  gains {gain}')
