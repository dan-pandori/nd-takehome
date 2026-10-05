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
