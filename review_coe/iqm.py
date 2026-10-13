#!/usr/bin/env python3
"""Reviewer: IQM (scipy trim_mean 0.25, as rliable) with a percentile-bootstrap 95 % interval over seeds (10,000 resamples,
seeded) for the headline per-seed quantities (strict held-out members solved of 106, r16 x0 / pend x0) and the full - knockout
difference of IQMs."""
import json, os, sys
import numpy as np
from scipy.stats import trim_mean
A = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'out_acq.json')))['reads']
rng = np.random.default_rng(20261013)
def vals(ck, arm, seeds): return np.array([A[f'{ck}_{arm}_s{s}_x0']['strict']['solved'] for s in seeds], float)
def boot(x, B=10000):
    idx = rng.integers(0, len(x), (B, len(x))); return np.percentile([trim_mean(x[i], 0.25) for i in idx], [2.5, 97.5])
for ck in ('pend', 'r16'):
    F = vals(ck, 'full', range(6)); K = vals(ck, 'ko', range(6)); D = vals(ck, 'dose1', range(3))
    for nm, x in (('full', F), ('knockout', K), ('dose1', D)):
        lo, hi = boot(x)
        print(f'{ck} {nm:8s} per seed {x.astype(int).tolist()}  IQM {trim_mean(x, 0.25):.2f}  95% CI [{lo:.2f}, {hi:.2f}]')
    d = [trim_mean(F[rng.integers(0, 6, 6)], 0.25) - trim_mean(K[rng.integers(0, 6, 6)], 0.25) for _ in range(10000)]
    print(f'{ck} full - knockout IQM difference {trim_mean(F, 0.25) - trim_mean(K, 0.25):.2f}  95% CI {np.percentile(d, [2.5, 97.5]).round(2).tolist()}')
