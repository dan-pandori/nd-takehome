#!/usr/bin/env python3
"""Reviewer: Q12 pretraining-compute equivalent.  (a) set level: my IRT theta vs ln(step) over p3000..pend, extrapolated to
theta_r8 (multiplier = step / pretraining steps).  (b) per theorem in B (eqk r8 x0): teacher-forced log pi of r8's eventual
proof (trajectory tj_score, 33 bases, T 1.0 and T 0.8) vs ln(step) over p3000..pend, extrapolated to its r8 value."""
import json, os, sys, math
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rv_load as L
IRT = json.load(open(f'{L.RV}/review_cd/out_irt.json'))
S = json.load(open(f'{L.RV}/review_cd/out_sets.json'))
TC = json.load(open(os.path.expanduser('~/work/trajectory/artifacts/tj/compute.json')))
LATE = ['p3000', 'p5000', 'p8000', 'p12000', 'p16000', 'p20000', 'pend']
for s in (0, 1, 2):
    end = TC[f'stage1|{s}']['train_steps']
    st = {**L.STEPS, 'pend': end}
    xs = np.array([math.log(st[c]) for c in LATE]); ys = np.array([IRT[str(s)]['pt'][c] for c in LATE])
    b, a = np.polyfit(xs, ys, 1)
    mult = {ck: math.exp((IRT[str(s)]['rl'][key] - a) / b) / end for ck, key in (('r8', 'r8_01'), ('r16', 'r16_1'))}
    print(f's{s}: (a) IRT theta slope {b:.3f} per e-fold; multiplier r8 {mult["r8"]:,.1f}x, r16 {mult["r16"]:,.1f}x (pretraining {end} steps)')
    # (b) per theorem
    D = os.path.expanduser(f'~/work/trajectory/artifacts/tj/score/s{s}')
    ev = {}
    for ck in LATE + ['r8']:
        for r in L.rows(f'{D}/s{s}_{ck}.jsonl'):
            if r['tid'].startswith('ev:'):
                ev.setdefault(r['tid'][3:], {})[ck] = (r['T1.0']['total'], r['T0.8']['total'])
    for ti, T in ((0, 'T1.0'), (1, 'T0.8')):
        m = []; neg = 0
        for n in S['eqk'][f's{s}_r8_x0']:
            if n not in ev: continue
            y = np.array([ev[n][c][ti] for c in LATE]); bb, aa = np.polyfit(xs, y, 1)
            target = ev[n]['r8'][ti]
            if bb <= 0: neg += 1; m.append(math.inf); continue
            m.append(math.exp((target - aa) / bb) / end)
        m = np.array(m)
        print(f'     (b) per theorem, ev proof log pi {T}: n {len(m)}, median multiplier {np.median(m):,.1f}x '
              f'[IQR {np.percentile(m, 25):,.1f}-{np.percentile(m, 75):,.1f}]; non-improving trend (inf) {neg}; share in 3-30x {np.mean((m >= 3) & (m <= 30)):.2f}')
