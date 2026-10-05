#!/usr/bin/env python3
"""Reviewer: IRT at matched ability gain (the irt-ability critic's design), own 2PL fit.  Calibrate items on pretraining
checkpoints p0 ... S (3 seeds, x0 + x1); project with items fixed: the later pretraining checkpoints (continuation), EI
from S (rl-from-ckpt s<s>_<S>_r{2,4,8}; trajectory r1-r8 when S = pend) and the replay-only control c<s>_<S>_r8.
created = DIF+ (one-sided binomial tail < 1e-3 and smoothed log-odds residual > ln 10) on items S fails (0 / 512);
rate = created / (S-failed items the arm solves at p-hat >= 0.05)."""
import json, os, sys, math
import numpy as np
from scipy.optimize import minimize
from scipy.special import expit, log_expit
from scipy.stats import binom
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rv_load as L
N = L.names(); I = len(N); idx = {n: i for i, n in enumerate(N)}
def counts(s, key):
    c = np.zeros(I); n = np.zeros(I)
    for x in (0, 1):
        for pool in ('tb72', 'h250'):
            p = f'{L.RFC}/{key}__{pool}_x{x}.jsonl' if key.startswith(('s', 'c')) and '_r' in key and key[1].isdigit() and '_p' in key or key.startswith('c') else L.path(12, s, key, pool, x)
            if p is None or not os.path.exists(p): return None
            for r in L.rows(p):
                c[idx[r['name']]] += r['n_ok']; n[idx[r['name']]] += r['n_tried']
    return c, n
def fit(C, NN):
    M = len(C)
    def nlp(w):
        th, al, b = w[:M], w[M:M + I], w[M + I:]; a = np.exp(al)
        z = a[None, :] * (th[:, None] - b[None, :])
        g = C - NN * expit(z)
        f = (C * log_expit(z) + (NN - C) * log_expit(-z)).sum() - (th ** 2).sum() / 32 - (b ** 2).sum() / 32 - (al ** 2).sum() / 0.5
        return -f, -np.concatenate([(g * a[None, :]).sum(1) - th / 16, (g * (th[:, None] - b[None, :])).sum(0) * a - al / 0.25, -(g * a[None, :]).sum(0) - b / 16])
    r = minimize(nlp, np.concatenate([np.linspace(-2, 2, M), np.zeros(I), np.zeros(I)]), jac=True, method='L-BFGS-B', options={'maxiter': 20000, 'maxfun': 50000})
    return np.exp(r.x[M:M + I]), r.x[M + I:]
def project(c, n, a, b):
    def f(t):
        z = a * (t[0] - b)
        return -(c * log_expit(z) + (n - c) * log_expit(-z)).sum() + t[0] ** 2 / 32, -np.array([((c - n * expit(z)) * a).sum() - t[0] / 16])
    return minimize(f, np.array([0.0]), jac=True, method='L-BFGS-B').x[0]
PT = L.PT
for start in sys.argv[1:] or ['p5000']:
    upto = PT[:PT.index(start) + 1]
    cal = [counts(s, ck) for s in (0, 1, 2) for ck in upto]
    a, b = fit(np.array([c for c, n in cal]), np.array([n for c, n in cal]))
    print(f'=== calibration through {start} ({len(cal)} examinees) ===')
    for s in (0, 1, 2):
        c0, n0 = counts(s, start); t0 = project(c0, n0, a, b); failed = c0 == 0
        arms = [(f'PT {ck}', ck) for ck in PT[PT.index(start) + 1:]]
        if start == 'pend':
            arms += [(f'EI {r}', r) for r in ('r1', 'r2', 'r4', 'r8')] + [('replay r8', f'c{s}_pend_r8')]
        else:
            arms += [(f'EI r{r}', f's{s}_{start}_r{r}') for r in (2, 4, 8)] + [('replay r8', f'c{s}_{start}_r8')]
        out = []
        for lab, key in arms:
            cn = counts(s, key)
            if cn is None: out.append(f'{lab} missing'); continue
            c, n = cn; t = project(c, n, a, b); p = expit(a * (t - b))
            tail = np.array([binom.sf(ci - 1, ni, pi) if ci > 0 else 1.0 for ci, ni, pi in zip(c, n, p)])
            res = np.log((c + .5) / (n - c + .5)) - np.log(p / (1 - p))
            difp = (tail < 1e-3) & (res > math.log(10))
            cr = int((difp & failed).sum()); den = int((failed & (c / n >= 0.05)).sum())
            out.append(f'{lab} dθ {t - t0:+.2f} created {cr} rate {cr / den if den else float("nan"):.2f}')
        print(f'  s{s}: ' + ' | '.join(o for o in out if o.startswith(('PT pend', 'EI', 'replay')) or start == 'pend'))
