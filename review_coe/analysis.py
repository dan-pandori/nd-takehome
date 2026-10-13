#!/usr/bin/env python3
"""Reviewer: derived quantities from out_acq.json -- families acquired DURING RL (at r16 but not at pend, same draw),
robustness of the primary indicator to the x1 redraw and the guided read, the extension reads (ko s1 r20 / r24),
seed-level medians, and the exact tests on those."""
import json, os, statistics, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as C
RV = C.RV
A = json.load(open(f'{RV}/review_coe/out_acq.json'))['reads']
FAMS = ['contraposition_conv', 'demorgan_nand_to_or', 'excluded_middle', 'negated_conditional', 'peirce', 'peirce_sequent']
import math


def fisher(x1, n1, x2, n2):
    m = x1 + x2; N = n1 + n2
    return sum(math.comb(n1, k) * math.comb(n2, m - k) for k in range(x1, min(n1, m) + 1)) / math.comb(N, m)


def boschloo(x1, n1, x2, n2, grid=2001):
    pobs = fisher(x1, n1, x2, n2)
    crit = [(a, b) for a in range(n1 + 1) for b in range(n2 + 1) if fisher(a, n1, b, n2) <= pobs + 1e-12]
    return max(sum(math.comb(n1, a) * p ** a * (1 - p) ** (n1 - a) * math.comb(n2, b) * p ** b * (1 - p) ** (n2 - b) for a, b in crit)
               for p in [i / (grid - 1) for i in range(grid)])


def acq(tag):
    return set(A[tag]['strict']['acquired']) if tag in A else None


print('== families acquired during RL (strict, x0: acquired at r16, not at pend)')
during = {}
for arm, seeds in (('full', range(6)), ('ko', range(6)), ('dose1', range(3))):
    for s in seeds:
        p = acq(f'pend_{arm}_s{s}_x0'); r = acq(f'r16_{arm}_s{s}_x0')
        d = sorted(r - p); during[(arm, s)] = d
        print(f'  {arm}_s{s}: pend {sorted(p)} -> r16 {sorted(r)}; during RL: {d}')
f = sum(1 for s in range(6) if during[('full', s)]); k = sum(1 for s in range(6) if during[('ko', s)])
print(f'  seeds with >= 1 family acquired during RL: full {f}/6, knockout {k}/6; Boschloo one-sided p = {boschloo(f, 6, k, 6):.4f}')
dd = sum(1 for s in range(3) if during[('dose1', s)])
print(f'  dose1 {dd}/3; dose1 vs knockout Boschloo p = {boschloo(dd, 3, k, 6):.4f}')
print('== primary indicator on other draws / reads (r16)')
for dr in ('x0', 'x1', 'g0'):
    fi = [1 if acq(f'r16_full_s{s}_{dr}') else 0 for s in range(6) if acq(f'r16_full_s{s}_{dr}') is not None]
    ki = [1 if acq(f'r16_ko_s{s}_{dr}') else 0 for s in range(6) if acq(f'r16_ko_s{s}_{dr}') is not None]
    print(f'  r16 {dr}: full {sum(fi)}/{len(fi)}, knockout {sum(ki)}/{len(ki)}; Boschloo p {boschloo(sum(fi), len(fi), sum(ki), len(ki)):.5f}')
print('== pend indicator (bases)')
for dr in ('x0', 'x1', 'g0'):
    fi = [1 if acq(f'pend_full_s{s}_{dr}') else 0 for s in range(6)]
    ki = [1 if acq(f'pend_ko_s{s}_{dr}') else 0 for s in range(6)]
    di = [1 if acq(f'pend_dose1_s{s}_{dr}') else 0 for s in range(3)]
    print(f'  pend {dr}: full {fi}, knockout {ki}, dose1 {di}')
print('== strict held-out solved (of 106), per seed: pend x0 -> r8 x0 -> r16 x0 / x1 / g0')
for arm, seeds in (('full', range(6)), ('ko', range(6)), ('dose1', range(3))):
    for s in seeds:
        v = [A.get(f'{c}_{arm}_s{s}_{d}', {}).get('strict', {}).get('solved') for c, d in (('pend', 'x0'), ('r8', 'x0'), ('r16', 'x0'), ('r16', 'x1'), ('r16', 'g0'))]
        ex = '' if (arm, s) != ('ko', 1) else f'  r20 {A["r20_ko_s1_x0"]["strict"]["solved"]} r24 {A["r24_ko_s1_x0"]["strict"]["solved"]} (contraposition_conv {A["r20_ko_s1_x0"]["strict"]["per_family"]["contraposition_conv"]}, {A["r24_ko_s1_x0"]["strict"]["per_family"]["contraposition_conv"]})'
        print(f'  {arm}_s{s}: {v}{ex}')
for arm, seeds in (('full', range(6)), ('ko', range(6)), ('dose1', range(3))):
    xs = [A[f'r16_{arm}_s{s}_x0']['strict']['solved'] for s in seeds]
    print(f'  {arm}: r16 x0 strict solved {xs} median {statistics.median(xs)}')
print('== per family, seeds acquiring at r16 (x0)')
for fm in FAMS:
    cnt = {}
    for lab, arm, seeds in (('full', 'full', range(6)), ('full_old', 'full', range(3)), ('full_new', 'full', range(3, 6)), ('ko', 'ko', range(6)), ('dose1', 'dose1', range(3))):
        cnt[lab] = f'{sum(1 for s in seeds if fm in (acq(f"r16_{arm}_s{s}_x0") or set()))}/{len(seeds)}'
    print(f'  {fm:22s} ' + ' '.join(f'{k} {v}' for k, v in cnt.items()))
