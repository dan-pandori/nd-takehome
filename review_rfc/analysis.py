#!/usr/bin/env python3
"""Reviewer threshold analysis (rl-from-ckpt), own code.  x = worst-step log p (min of the per-step T1.0 log p list in
the score files; I take the min myself rather than the stored `w1`), clipped at -40.  y = solved at k 256 sample seed 1.
Logistic fits by Newton-Raphson (numpy).  Null = end arm (trajectory's best-cap12 r8 x1 vs x_start at pend)."""
import json, os, collections, sys, random
import numpy as np
R = os.path.expanduser('~/review/rl-from-ckpt'); SC = f'{R}/artifacts/rfc/score'
TJS = os.path.expanduser('~/review/trajectory/artifacts/tj/score')
rc = json.load(open(f'{R}/review_rfc/rv/recount.json'))['solved']
STARTS = ['p1600', 'p5000', 'p12000', 'p16000']
def scores(fn, kind='ref'):
    d = {}
    for l in open(fn):
        r = json.loads(l)
        if r['tid'].startswith(kind + ':'):
            d[r['tid'].split(':', 1)[1]] = max(-40.0, min(r['T1.0']['step_lp']))
    return d
xs, xc, xl = {}, {}, {}
for s in (0, 1, 2):
    for st in STARTS + ['pend']:
        xs[s, st] = scores(f'{TJS}/s{s}/s{s}_{st}.jsonl')
        xc[s, st] = scores(f'{SC}/s{s}_{st}/s{s}_{st}_c8.jsonl' if st != 'pend' else f'{SC}/cpend_s{s}/s{s}_pend_c8.jsonl')
        if st != 'pend':
            for c in ('r0', 'r2', 'r4', 'r8'): xl[s, st, c] = scores(f'{SC}/s{s}_{st}/s{s}_{st}_{c}.jsonl')
NAMES = sorted(xs[0, 'pend'])
print('ref theorems', len(NAMES), {k: len(v) for k, v in list(xc.items())[:3]})
# re-score check: this run's r0 (= start) vs trajectory's score of the same checkpoint
d = [abs(xl[s, st, 'r0'][n] - xs[s, st][n]) for s in (0, 1, 2) for st in STARTS for n in NAMES]
print(f'r0 rescore vs trajectory: max |dx| {max(d):.2e}, n {len(d)}, >1e-3: {sum(x > 1e-3 for x in d)}')
def y(s, st, x='x1', ck='r8'):
    k = f'T s{s} {ck} tb72 {x}' if st == 'pend' else f'L s{s} {st} {ck} tb72 {x}'
    return set(rc[k]) | set(rc[k.replace('tb72', 'h250')])
def fit(X, Y, fe=None):
    """logistic; fe: list of group ids -> separate intercepts.  returns params (intercepts..., slope)."""
    X = np.asarray(X, float); Y = np.asarray(Y, float)
    g = np.zeros(len(X), int) if fe is None else np.asarray(fe)
    G = g.max() + 1; A = np.zeros((len(X), G + 1)); A[np.arange(len(X)), g] = 1; A[:, G] = X
    b = np.zeros(G + 1)
    for _ in range(100):
        p = 1 / (1 + np.exp(-A @ b)); W = p * (1 - p) + 1e-12
        H = A.T @ (A * W[:, None]) + 1e-9 * np.eye(G + 1); st = np.linalg.solve(H, A.T @ (Y - p)); b += st
        if np.abs(st).max() < 1e-10: break
    return b
def P(b0, b1, x): return 1 / (1 + np.exp(-(b0 + b1 * np.asarray(x))))
# null: end arm
Xn, Yn, Gn = [], [], []
for s in (0, 1, 2):
    ys = y(s, 'pend')
    for n in NAMES: Xn.append(xs[s, 'pend'][n]); Yn.append(n in ys); Gn.append(s)
b = fit(Xn, Yn); print(f'null (end arm, pooled, no FE): b0 {b[0]:.3f} b1 {b[1]:.3f} x50 {-b[0]/b[1]:.2f}')
NULL = (b[0], b[1])
for s in (0, 1, 2):
    m = [i for i in range(len(Xn)) if Gn[i] == s]; bs = fit([Xn[i] for i in m], [Yn[i] for i in m])
    print(f'  seed {s}: b0 {bs[0]:.3f} b1 {bs[1]:.3f} x50 {-bs[0]/bs[1]:.2f}  solved {sum(Yn[i] for i in m)}/{len(m)}')
PRE = (5.34, 0.482)
def boot_x50(X, Y, G, B=400, seed=0):
    rng = np.random.default_rng(seed); X = np.asarray(X); Y = np.asarray(Y); G = np.asarray(G); out = []
    idx = {g: np.where(G == g)[0] for g in set(G.tolist())}
    for _ in range(B):
        ii = np.concatenate([rng.choice(v, len(v)) for v in idx.values()])
        bb = fit(X[ii], Y[ii], G[ii]); out.append(np.mean([-bb[g] / bb[-1] for g in idx]))
    return np.percentile(out, [2.5, 97.5])
for form, XX in (('x_start', xs), ('x_ctrl', xc)):
    print(f'\n## form {form}: fits of P(y=ladder r8 x1 | x)  [x clipped -40]')
    tot = collections.Counter()
    for st in STARTS + ['pend']:
        X, Y, G = [], [], []
        per = []
        for s in (0, 1, 2):
            ys = y(s, st)
            Xs = [XX[s, st][n] for n in NAMES]; Ys = [n in ys for n in NAMES]
            bs = fit(Xs, Ys); per.append(-bs[0] / bs[1])
            X += Xs; Y += Ys; G += [s] * len(NAMES)
            low = [i for i, v in enumerate(Xs) if v < -12]
            for nm, nb in (('pre', PRE), ('mine', NULL)):
                e = sum(Ys[i] for i in low) - float(P(*nb, [Xs[i] for i in low]).sum())
                if st != 'pend': tot[nm, s] += e; tot[nm, 'n', s] += len(low); tot[nm, 'y', s] += sum(Ys[i] for i in low); tot[nm, 'exp', s] += float(P(*nb, [Xs[i] for i in low]).sum())
            print(f'  {st} s{s}: x50 {per[-1]:7.2f}  b1 {bs[1]:.3f}  pairs x<-12: {len(low):3d} solved {sum(Ys[i] for i in low):3d} '
                  f'null-exp(pre) {float(P(*PRE, [Xs[i] for i in low]).sum()):5.1f} excess(pre) {sum(Ys[i] for i in low) - float(P(*PRE, [Xs[i] for i in low]).sum()):+5.1f}')
        bf = fit(X, Y, G); x50fe = [-bf[g] / bf[-1] for g in (0, 1, 2)]
        ci = boot_x50(X, Y, G, B=200)
        print(f'  {st} pooled seed-FE: slope {bf[-1]:.3f}, x50 per seed {[round(v, 2) for v in x50fe]}, mean {np.mean(x50fe):.2f} '
              f'[{ci[0]:.2f}, {ci[1]:.2f}] (theorem bootstrap within seed); per-seed-fit mean {np.mean(per):.2f}')
    for nm in ('pre', 'mine'):
        E = [tot[nm, s] for s in (0, 1, 2)]
        print(f'  EXCESS over p1600-p16000 ({nm} null): per seed {[round(e, 1) for e in E]} total {sum(E):.1f}; '
              f'pairs {[tot[nm, "n", s] for s in (0, 1, 2)]} solved {[tot[nm, "y", s] for s in (0, 1, 2)]} expected {[round(tot[nm, "exp", s], 1) for s in (0, 1, 2)]}')
# null expectation over x_start < -12 as the prereg states (from x_start at each start)
print('\n## prereg null table check (x_start<-12 pairs, expected under pre-reg null)')
for st in STARTS + ['pend']:
    low = [(s, n) for s in (0, 1, 2) for n in NAMES if xs[s, st][n] < -12]
    print(st, len(low), round(float(P(*PRE, [xs[s, st][n] for s, n in low]).sum()), 1))
# group C
print('\n## group C (trajectory end arm: neither pend nor r8 solves, x0 reads); r8 x1 solves')
allnames = set(rc['T s0 pend tb72 x0']) | set()
POOL = [json.loads(l)['name'] for f in ('textbook72', 'holdout250') for l in open(f'{R}/data/bs/{f}.jsonl')]
Cs = {}
for s in (0, 1, 2):
    sol0 = y(s, 'pend', 'x0', 'pend'); sol8 = y(s, 'pend', 'x0', 'r8')
    Cs[s] = [n for n in POOL if n not in sol0 and n not in sol8]
for st in STARTS + ['pend']:
    v = [len(set(Cs[s]) & y(s, st)) for s in (0, 1, 2)]
    print(f'  {st}: C solved at r8 x1 per seed {v} of {[len(Cs[s]) for s in (0, 1, 2)]} (sum {sum(v)})')
# symmetric only-A / only-B over both sample seeds: early start ladder vs end arm
print('\n## symmetric: theorems solved by ladder(start) r8 in both x0,x1 and by end arm r8 in neither, and vice versa')
for st in STARTS:
    a = b_ = 0
    for s in (0, 1, 2):
        L0, L1 = y(s, st, 'x0'), y(s, st, 'x1'); E0, E1 = y(s, 'pend', 'x0'), y(s, 'pend', 'x1')
        a += len((L0 & L1) - (E0 | E1)); b_ += len((E0 & E1) - (L0 | L1))
    print(f'  {st}: only ladder {a}, only end arm {b_} (3 seeds pooled, 322 theorems each)')
json.dump({'xs': {f'{k[0]}|{k[1]}': v for k, v in xs.items()}, 'xc': {f'{k[0]}|{k[1]}': v for k, v in xc.items()}}, open(f'{R}/review_rfc/rv/x.json', 'w'))
