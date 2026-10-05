#!/usr/bin/env python3
"""Reviewer: Q16 extrapolation backtest, two versions.
(1) As pre-registered: support-curves stage s1/s3 (3.2 M lean_seq models: WP base and EI r8, seeds 0 / 1; 383 theorems,
    10,000 attempts each, stop at 50 successes).  The rows hold counts, not attempt sequences, so the count in "the first
    256 attempts" is drawn by hypergeometric thinning (exchangeable attempts: exact in distribution), 50 replicates.
    Beta-binomial (and zero-inflated BB) fitted by ML on (c256, 256) over all 383; predicted number solved at 10,000 =
    sum_t P(>= 1 success in 10,000 | c256_t).  Compared with the observed number with n_ok > 0.
(2) The executor's adaptation: pend_s small sample (x0 + x1 + x2 [+ x4 for C]) over 322 theorems -> predict the J2
    theorems with >= 1 success in J2 stage A's 16,384 fresh attempts."""
import json, os, sys, glob, math
import numpy as np
from scipy.optimize import minimize
from scipy.special import betaln, gammaln
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rv_load as L
rng = np.random.default_rng(16)
def ll_bb(c, n, a, b): return gammaln(n + 1) - gammaln(c + 1) - gammaln(n - c + 1) + betaln(c + a, n - c + b) - betaln(a, b)
def fit(c, n, zi):
    def nll(v):
        a, b = np.exp(v[0]), np.exp(v[1]); l = ll_bb(c, n, a, b)
        if zi:
            z = 1 / (1 + np.exp(-v[2])); l = np.where(c == 0, np.logaddexp(np.log(z), np.log1p(-z) + l), np.log1p(-z) + l)
        return -l.sum()
    best = None
    for v0 in ([-1.0, 1.0, -1.0], [-2.0, 3.0, 0.0], [0.0, 5.0, 1.0], [-3.0, 0.0, 0.5]):
        r = minimize(nll, np.array(v0[:3 if zi else 2]), method='Nelder-Mead', options={'maxiter': 8000, 'xatol': 1e-7, 'fatol': 1e-9})
        if best is None or r.fun < best.fun: best = r
    a, b = np.exp(best.x[0]), np.exp(best.x[1]); z = 1 / (1 + np.exp(-best.x[2])) if zi else 0.0
    return a, b, z
def p_solved(c, n, m, a, b, z):
    """P(>= 1 success in m further attempts | c of n), solved already if c > 0"""
    q = 1 - np.exp(betaln(a + c, b + n - c + m) - betaln(a + c, b + n - c))     # P(hit in m | non-zero class)
    if z > 0:
        pz = z / (z + (1 - z) * np.exp(betaln(a, b + n) - betaln(a, b)))
        q = np.where(c == 0, (1 - pz) * q, q)
    return np.where(c > 0, 1.0, q)
print('(1) support-curves, as pre-registered (383 theorems; first 256 by hypergeometric thinning, 50 replicates)')
D = f'{L.RV}/review_cd/sc'
for lab, pre in (('WP base s0', 's1_base_T08_s0'), ('WP EI s0', 's1_ei_T08_s0'), ('WP base s1', 's3_base_T08_s1'), ('WP EI s1', 's3_ei_T08_s1')):
    rows = [json.loads(l) for p in sorted(glob.glob(f'{D}/{pre}.s*.jsonl')) for l in open(p)]
    N = np.array([r['n_tried'] for r in rows]); K = np.array([r['n_ok'] for r in rows])
    obs = int((K > 0).sum())
    errs = {False: [], True: []}
    for rep in range(50):
        c = rng.hypergeometric(K, N - K, np.minimum(256, N))
        n = np.full(len(c), 256)
        for zi in (False, True):
            a, b, z = fit(c, n, zi)
            pred = p_solved(c, n, 10000 - 256, a, b, z).sum()
            errs[zi].append((pred - obs) / obs)
    e0, e1 = np.array(errs[False]), np.array(errs[True])
    print(f'  {lab:11s}: observed solved@10,000 {obs}/383; BB rel. error median {np.median(e0):+.3f} [{np.percentile(e0, 5):+.3f}, {np.percentile(e0, 95):+.3f}]; '
          f'within +-25 % in {np.mean(np.abs(e0) <= 0.25):.2f} of replicates;  ZIBB median {np.median(e1):+.3f} [{np.percentile(e1, 5):+.3f}, {np.percentile(e1, 95):+.3f}], '
          f'|ZIBB| <= |BB| in {np.mean(np.abs(e1) <= np.abs(e0) + 1e-12):.2f}')
print('\n(2) executor adaptation: pend small sample -> J2 stage A (16,384 fresh attempts) on J2 theorems')
EX = json.load(open(f'{L.CD}/j1/sets.json'))
for s in (0, 1, 2):
    c = {}; n = {}
    for x in (0, 1, 2):
        for k, v in L.both(12, s, 'pend', x).items(): c[k] = c.get(k, 0) + v[0]; n[k] = n.get(k, 0) + v[1]
    for k, v in L.read(12, s, 'pend', 'C', 4).items(): c[k] += v[0]; n[k] += v[1]
    names = L.names(); cc = np.array([c[k] for k in names]); nn = np.array([n[k] for k in names])
    A = {}
    for p in glob.glob(f'{L.CD}/j2/s{s}_c0*.jsonl'):
        for r in L.rows(p): A[r['name']] = (r['n_ok'], r['n_tried'])
    J2 = EX[str(s)]['J2']; obs = sum(A[t][0] > 0 for t in J2)
    idx = [names.index(t) for t in J2]
    out = []
    for zi in (False, True):
        a, b, z = fit(cc, nn, zi)
        q = 1 - np.exp(betaln(a + cc[idx], b + nn[idx] - cc[idx] + 16384) - betaln(a + cc[idx], b + nn[idx] - cc[idx]))
        if zi:
            pz = z / (z + (1 - z) * np.exp(betaln(a, b + nn[idx]) - betaln(a, b)))
            q = np.where(cc[idx] == 0, (1 - pz) * q, q)
        out.append(q.sum())
    print(f'  s{s}: J2 theorems {len(J2)} (small-sample successes on them: {int(cc[idx].sum())}); observed >= 1 in 16,384: {obs}; BB predicts {out[0]:.1f} ({(out[0] - obs) / obs:+.2f}); ZIBB {out[1]:.1f} ({(out[1] - obs) / obs:+.2f})')
