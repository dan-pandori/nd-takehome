#!/usr/bin/env python3
"""rl-from-ckpt: numbers the pre-registration rests on, from trajectory's inherited records (inherit/tj, fetched by
rfc_fetch.sh).  Model: trajectory's best-cap12 seeds 0-2 (ALiBiGPT 9,560,832 params, lean_staten, from scratch on K12).
x = reference worst-step log p (T 1.0, nats) under each start checkpoint; y = solved (n_ok > 0 of 256, sample seed 1)."""
import json, math, collections, statistics as st
I = 'inherit/tj'
STARTS = ['p0', 'p1600', 'p5000', 'p12000', 'p16000', 'pend']
def rj(p): return [json.loads(l) for l in open(p) if l.strip()]
def solved(s, ck, x):
    out = {}
    for pool in ('tb72', 'h250'):
        for r in rj(f'{I}/eval/s{s}_{ck}__{pool}_x{x}.jsonl'):
            out[r['name']] = (r['n_ok'] > 0, pool)
    return out
def xref(s, ck):
    out = {}
    for sub in (f's{s}', f'new8_s{s}'):
        try: rows = rj(f'{I}/score/{sub}/s{s}_{ck}.jsonl')
        except FileNotFoundError: continue
        for o in rows:
            if o['tid'].startswith('ref:'):
                out[o['tid'][4:]] = o['T1.0']['w1']
    return out
print('start  seed  n_ref  med_x  #x<-12  #x<-8  #x<-6 | solved@start x1 tb72/h250 | end-ladder r8 x1 solved with x<-12 at start')
rows = []
for ck in STARTS:
    for s in (0, 1, 2):
        X = xref(s, ck); y0 = solved(s, ck, 1); y8 = solved(s, 'r8', 1)
        xs = list(X.values())
        tb = sum(v for v, p in y0.values() if p == 'tb72' for v in [v]); hb = sum(v for v, p in y0.values() if p == 'h250')
        lo = [n for n, x in X.items() if x < -12]
        print(f'{ck:7s} {s}  {len(xs):4d} {st.median(xs):7.2f} {sum(x<-12 for x in xs):6d} {sum(x<-8 for x in xs):6d} {sum(x<-6 for x in xs):6d} | {tb:3d}/{hb:3d} | {sum(y8.get(n,(0,))[0] for n in lo)}')
# threshold of the end-of-pretraining ladder: P(r8 solves | x at pend), binned
print('\nend ladder (trajectory): P(r8 x1 solves | x_ref at pend), pooled over seeds')
bins = [(-99, -12), (-12, -8), (-8, -6), (-6, -4), (-4, -2), (-2, 0.1)]
for s in (0, 1, 2):
    X = xref(s, 'pend'); y8 = solved(s, 'r8', 1)
    rows += [(x, y8[n][0]) for n, x in X.items() if n in y8]
for lo, hi in bins:
    ys = [y for x, y in rows if lo <= x < hi]
    print(f'  [{lo:4d},{hi:5.1f}) n={len(ys):4d} P={sum(ys)/max(1,len(ys)):.3f}')

# logistic fit of the end arm (x at pend -> r8 x1), per seed and pooled; null count of x<-12 solves at each start
import numpy as np
def logit_fit(x, y, iters=50):
    X = np.c_[np.ones(len(x)), x]; b = np.zeros(2)
    for _ in range(iters):
        p = 1 / (1 + np.exp(-X @ b)); W = p * (1 - p) + 1e-9
        b = b + np.linalg.solve(X.T @ (W[:, None] * X) + 1e-6 * np.eye(2), X.T @ (y - p))
    return b
print('\nend-arm logistic P(r8 x1 | x_ref at pend): b0, b1, x(P=0.5)')
fits = {}
for s in (0, 1, 2, 'all'):
    ss = (0, 1, 2) if s == 'all' else (s,)
    xs, ys = [], []
    for t in ss:
        X = xref(t, 'pend'); y8 = solved(t, 'r8', 1)
        for n, x in X.items():
            if n in y8: xs.append(max(x, -40)); ys.append(float(y8[n][0]))
    b = logit_fit(np.array(xs), np.array(ys)); fits[s] = b
    print(f'  seed {s}: b0 {b[0]:.2f} b1 {b[1]:.3f} x50 {-b[0]/b[1]:.1f}')
b = fits['all']
print('\nnull (end-arm pooled curve) expected solves among x<-12 pairs, per start (3 seeds summed); x clipped at -40')
for ck in STARTS:
    e = n = 0
    for s in (0, 1, 2):
        for nme, x in xref(s, ck).items():
            if x < -12:
                n += 1; e += 1 / (1 + math.exp(-(b[0] + b[1] * max(x, -40))))
    print(f'  {ck:7s} pairs {n:4d} expected {e:6.1f}')
# sample-seed concordance at r8 (end arm): pairs whose solved status differs between x0 and x1
d = t = 0
for s in (0, 1, 2):
    a0, a1 = solved(s, 'r8', 0), solved(s, 'r8', 1)
    d += sum(a0[n][0] != a1[n][0] for n in a0); t += len(a0)
print(f'\nend arm r8: solved status differs between sample seeds 0 and 1 in {d}/{t} theorem-seed pairs')

# group C (seed-0 samples: neither pend nor r8 solves) and how many of them r8 solves with sample seed 1
for s in (0, 1, 2):
    a0, b0, b1 = solved(s, 'pend', 0), solved(s, 'r8', 0), solved(s, 'r8', 1)
    C = [n for n in a0 if not a0[n][0] and not b0[n][0]]
    print(f'seed {s}: group C {len(C)}; r8 x1 solves {sum(b1[n][0] for n in C)}')
