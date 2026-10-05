#!/usr/bin/env python3
"""Reviewer's own binomial 2PL (MAP; theta ~ N(0,4^2), b ~ N(0,4^2), log a ~ N(0,0.5^2) -- the pre-registered card's
priors), written independently.  Examinees = (seed, checkpoint), counts pooled over draws x0 + x1 (r12 / r16: x1, and
r16 x0 from J5 where present -> report both), items = tb72 + h250 (322), all three seeds share item parameters.
Fit on pretraining checkpoints only (p0 ... pend, 14 x 3); project RL checkpoints and J7's continuation with items fixed.
Q8: Spearman(predicted p, observed rate) for r8; theta_r8 > every PT theta per seed; s1 r16 residual decile vs LEM items.
J7 (i): theta_cont between theta_pend + 0.5 and theta_r8."""
import json, os, sys, glob, math
import numpy as np
from scipy.optimize import minimize
from scipy.special import expit, log_expit
from scipy.stats import spearmanr, binom
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rv_load as L
N = L.names(); I = len(N); idx = {n: i for i, n in enumerate(N)}
def counts(s, ck, draws):
    c = np.zeros(I); n = np.zeros(I)
    for x in draws:
        d = L.both(12, s, ck, x)
        if d is None: return None
        for k, v in d.items(): c[idx[k]] += v[0]; n[idx[k]] += v[1]
    return c, n
def j7(s, draws=(0, 1)):
    c = np.zeros(I); n = np.zeros(I)
    for x in draws:
        for pool in ('tb72', 'h250'):
            for r in L.rows(f'{L.CD}/j7/s{s}_cont__{pool}_x{x}.jsonl'):
                c[idx[r['name']]] += r['n_ok']; n[idx[r['name']]] += r['n_tried']
    return c, n
ex = [(s, ck) for s in (0, 1, 2) for ck in L.PT]
C = np.array([counts(s, ck, (0, 1))[0] for s, ck in ex]); NN = np.array([counts(s, ck, (0, 1))[1] for s, ck in ex])
M = len(ex)
def unpack(w): return w[:M], w[M:M + I], w[M + I:]
def nlp(w):
    th, al, b = unpack(w); a = np.exp(al)
    z = a[None, :] * (th[:, None] - b[None, :])
    ll = C * log_expit(z) + (NN - C) * log_expit(-z)
    g = C - NN * expit(z)                      # d ll / d z
    dth = (g * a[None, :]).sum(1) - th / 16
    db = -(g * a[None, :]).sum(0) - b / 16
    dal = (g * (th[:, None] - b[None, :])).sum(0) * a - al / 0.25
    f = ll.sum() - (th ** 2).sum() / 32 - (b ** 2).sum() / 32 - (al ** 2).sum() / 0.5
    return -f, -np.concatenate([dth, dal, db])
w0 = np.concatenate([np.linspace(-2, 2, M), np.zeros(I), np.zeros(I)])
r = minimize(nlp, w0, jac=True, method='L-BFGS-B', options={'maxiter': 20000, 'maxfun': 50000})
print('PT fit:', r.message, 'nlp', round(r.fun, 2), 'iters', r.nit)
th, al, b = unpack(r.x); a = np.exp(al)
TH = {e: t for e, t in zip(ex, th)}
def project(c, n):
    def f(t):
        z = a * (t[0] - b)
        return -(c * log_expit(z) + (n - c) * log_expit(-z)).sum() + t[0] ** 2 / 32, -np.array([((c - n * expit(z)) * a).sum() - t[0] / 16])
    rr = minimize(f, np.array([0.0]), jac=True, method='L-BFGS-B')
    return rr.x[0]
out = {}
for s in (0, 1, 2):
    pts = [TH[(s, ck)] for ck in L.PT]
    print(f'\ns{s}: PT thetas ' + ' '.join(f'{ck}:{TH[(s, ck)]:.2f}' for ck in L.PT))
    rl = {}
    for ck, draws in [(f'r{i}', (0, 1)) for i in range(1, 9)] + [('r12', (1,)), ('r16', (1,)), ('r16', (0, 1))]:
        cn = counts(s, ck, draws)
        if cn is None: continue
        rl[(ck, draws)] = (project(*cn), cn)
    jc = j7(s); tj7 = project(*jc)
    print('   RL thetas ' + ' '.join(f'{ck}{"" if len(d) == 2 else "x1"}:{v[0]:.2f}' for (ck, d), v in rl.items()) + f'   J7 cont: {tj7:.2f}')
    t8, (c8, n8) = rl[('r8', (0, 1))]
    pred = expit(a * (t8 - b)); obs = c8 / n8
    rho = spearmanr(pred, obs).correlation
    print(f'   Q8a Spearman(pred, obs) r8: {rho:.3f};  Q8b theta_r8 {t8:.2f} > max PT {max(pts):.2f}: {t8 > max(pts)};  '
          f'J7 (i) theta_cont {tj7:.2f} in [pend+0.5 = {TH[(s, "pend")] + 0.5:.2f}, r8 {t8:.2f}]: {TH[(s, "pend")] + 0.5 <= tj7 <= t8}')
    out[s] = dict(pt={ck: TH[(s, ck)] for ck in L.PT}, rl={f'{ck}_{"".join(map(str, d))}': v[0] for (ck, d), v in rl.items()}, j7=tj7, rho=rho)
# Q8c: s1 r16 residuals vs the six holdout250 A v ~A instances
LEM6 = ['la_transfer_478', 'la_transfer_1572', 'la_transfer_956', 'la_transfer_795', 'la_transfer_1453', 'la_transfer_1424']
for draws in ((1,), (0, 1)):
    t16, (c, n) = (lambda v: v)(None or (project(*counts(1, 'r16', draws)), counts(1, 'r16', draws)))
    p = expit(a * (t16 - b))
    raw = c - n * p
    std = raw / np.sqrt(np.maximum(n * p * (1 - p), 1e-12))
    lo = np.log((c + 0.5) / (n - c + 0.5)) - np.log(p / (1 - p))
    tail = np.array([binom.sf(ci - 1, ni, pi) if ci > 0 else 1.0 for ci, ni, pi in zip(c, n, p)])
    for lab, v in (('raw count', raw), ('standardized', std), ('log-odds', lo), ('-log tail p', -np.log(np.maximum(tail, 1e-300)))):
        pos = np.where(raw > 0)[0]
        order_all = np.argsort(-v)
        top_all = set(order_all[:int(round(I / 10))])
        top_pos = set(pos[np.argsort(-v[pos])][:max(1, int(round(len(pos) / 10)))])
        k_all = sum(idx[n_] in top_all for n_ in LEM6); k_pos = sum(idx[n_] in top_pos for n_ in LEM6)
        print(f's1 r16 (draws {draws}, theta {t16:.2f}) residual {lab:13s}: LEM6 in top decile of all 322: {k_all}/6; in top decile of positive residuals ({len(pos)} items): {k_pos}/6')
json.dump({str(k): v for k, v in out.items()}, open(f'{L.RV}/review_cd/out_irt.json', 'w'), indent=1)

# Q8a variants: tie structure (many items at observed rate 0 or 1)
print('\nQ8a variants (r8, x0 + x1):')
for s in (0, 1, 2):
    t8, (c8, n8) = project(*counts(s, 'r8', (0, 1))), counts(s, 'r8', (0, 1))
    pred = expit(a * (t8 - b)); obs = c8 / n8
    m = (obs > 0) & (obs < 1)
    pc, nc = counts(s, 'pend', (0, 1)); pend_fail = pc == 0
    print(f'  s{s}: all {spearmanr(pred, obs).correlation:.3f}; 0<obs<1 ({m.sum()}) {spearmanr(pred[m], obs[m]).correlation:.3f}; '
          f'items pend fails ({pend_fail.sum()}) {spearmanr(pred[pend_fail], obs[pend_fail]).correlation:.3f}; '
          f'solved-indicator AUC-like rho {spearmanr(pred, obs > 0).correlation:.3f}; items at obs=1: {(obs == 1).sum()}, obs=0: {(obs == 0).sum()}')
