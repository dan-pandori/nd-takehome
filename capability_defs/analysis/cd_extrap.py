#!/usr/bin/env python3
"""capability-defs Part 3, Dan's (b) extrapolation: can pass@k beyond the sampled k be predicted?  Backtest on J2.

  python3 capability_defs/analysis/cd_extrap.py   -> out/extrap.txt (stdout), out/extrap.json

Small sample: pend_s's existing plain attempts per theorem (x0 + x1 + mcts-a x2, plus the x4 C-only read), ≈ 768.
Large sample: J2's fresh attempts (16,384 on the J2 theorems, which all had 0 successes in x0 + x1).
Models fitted on the small sample over all 322 theorems (per seed), by maximum likelihood:
  BB   p ~ Beta(a, b); c | n ~ BetaBinomial(n, a, b)                          (Kazdan et al. 2025)
  ZIBB with probability z, p = 0 exactly ("impossible"); else Beta(a, b)       (Kazdan et al. App. D.2 fix)
Prediction for each J2 theorem t (small-sample count c_t, n_t; J2 attempts m_t): P(>= 1 success in m_t | c_t, n_t),
from the posterior of p given the small sample.  Compared with J2's observed number of theorems with >= 1 success.
Pre-registered expectation Q16 (adapted: the pre-registration named the support-curves data, which hold no per-attempt
sequences): the BB prediction is within +/- 25 % of the observed count; ZIBB at least as close.
"""
import collections, glob, json, math, os, sys
import numpy as np
from scipy.optimize import minimize
from scipy.special import betaln, gammaln

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cd_reads as R

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..')
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'out')


def logbb(c, n, a, b):
    return gammaln(n + 1) - gammaln(c + 1) - gammaln(n - c + 1) + betaln(c + a, n - c + b) - betaln(a, b)


def fit(c, n, zi):
    def nll(v):
        a, b = np.exp(v[0]), np.exp(v[1])
        ll = logbb(c, n, a, b)
        if zi:
            z = 1 / (1 + np.exp(-v[2]))
            ll = np.where(c == 0, np.logaddexp(np.log(z), np.log1p(-z) + ll), np.log1p(-z) + ll)
        return -ll.sum()
    best = None
    for v0 in ([-1, 1, -1], [-2, 3, 0], [0, 5, 1]):
        r = minimize(nll, np.array(v0[:3 if zi else 2], float), method='Nelder-Mead', options={'maxiter': 4000, 'xatol': 1e-6, 'fatol': 1e-8})
        if best is None or r.fun < best.fun:
            best = r
    a, b = np.exp(best.x[0]), np.exp(best.x[1])
    z = 1 / (1 + np.exp(-best.x[2])) if zi else 0.0
    return a, b, z, best.fun


def p_hit(c, n, m, a, b, z):
    """P(>= 1 success in m more attempts | c of n) under (Z)IBB posterior."""
    # posterior of p | c, n is Beta(a + c, b + n - c) (non-zero branch); P(0 in m) = B(a+c, b+n-c+m) / B(a+c, b+n-c)
    p0_nonzero = math.exp(betaln(a + c, b + n - c + m) - betaln(a + c, b + n - c))
    if z == 0 or c > 0:
        return 1 - p0_nonzero
    # c == 0: posterior weight on the zero branch
    lz = math.log(z); lnz = math.log1p(-z) + float(logbb(0, n, a, b))
    w0 = 1 / (1 + math.exp(lnz - lz))
    return (1 - w0) * (1 - p0_nonzero)


def main():
    T = json.load(open(f'{OUT}/table_c12.json'))
    names = T['names']
    out = {}
    for s in R.SEEDS:
        S = T['seeds'][str(s)]
        small = {}
        for n_ in names:
            c = n = 0
            for x, v in S[n_]['counts'].get('pend', {}).items():
                c += v[0]; n += v[1]
            small[n_] = (c, n)
        J2 = collections.defaultdict(lambda: [0, 0])
        for p in glob.glob(f'{ROOT}/artifacts/cd/j2/s{s}_c*.jsonl'):
            for l in open(p):
                r = json.loads(l); J2[r['name']][0] += r['n_ok']; J2[r['name']][1] += r['n_tried']
        if not J2:
            print(f's{s}: no J2 stage-A files yet'); continue
        c = np.array([small[n][0] for n in names], float); n = np.array([small[n][1] for n in names], float)
        res = {}
        for lab, zi in (('BB', False), ('ZIBB', True)):
            a, b, z, nll = fit(c, n, zi)
            pred = sum(p_hit(small[t][0], small[t][1], J2[t][1], a, b, z) for t in J2)
            res[lab] = {'a': a, 'b': b, 'z': z, 'nll': nll, 'pred_hits': pred}
        obs = sum(1 for t in J2 if J2[t][0] > 0)
        hard = [t for t in J2 if small[t][0] == 0]
        for lab, zi in (('BB', False), ('ZIBB', True)):
            m = res[lab]
            m['pred_hard'] = sum(p_hit(small[t][0], small[t][1], J2[t][1], m['a'], m['b'], m['z']) for t in hard)
        obs_hard = sum(1 for t in hard if J2[t][0] > 0)
        print(f'  s{s} hard theorems only (0 successes in the small sample): {len(hard)}; observed hits {obs_hard}; '
              f'predicted BB {res["BB"]["pred_hard"]:.1f}, ZIBB {res["ZIBB"]["pred_hard"]:.1f}')
        out[s] = {'models': res, 'observed_hits': obs, 'n_theorems': len(J2), 'hard': len(hard), 'observed_hard': obs_hard}
        print(f's{s}: J2 theorems {len(J2)}; observed with >= 1 success {obs}; predicted BB {res["BB"]["pred_hits"]:.1f} '
              f'(a {res["BB"]["a"]:.3f}, b {res["BB"]["b"]:.2f}), ZIBB {res["ZIBB"]["pred_hits"]:.1f} (zero share {res["ZIBB"]["z"]:.3f}); '
              f'BB error {(res["BB"]["pred_hits"] - obs) / max(obs, 1):+.0%}, ZIBB error {(res["ZIBB"]["pred_hits"] - obs) / max(obs, 1):+.0%}')
    json.dump(out, open(f'{OUT}/extrap.json', 'w'), default=float)


if __name__ == '__main__':
    main()
