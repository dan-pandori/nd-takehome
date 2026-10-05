#!/usr/bin/env python3
"""capability-defs Part 3, definition P1 (IRT ability): binomial 2PL over checkpoint x theorem success counts.

  python3 capability_defs/analysis/cd_irt.py [--cap 12] > capability_defs/analysis/out/irt_c12.txt

Data: every plain read of tb72 + h250 (322 items) for one cap (cd_reads): examinee = (seed, checkpoint), counts pooled
over that checkpoint's draws (x0 + x1 = 512 for trajectory checkpoints; x1 = 256 for r12 / r16).  init (p0) and p50 /
p100 solve nothing; they are kept (the priors keep their ability finite).

Model: P(success of one attempt by examinee m on item i) = sigmoid(a_i * (theta_m - b_i)); counts ~ Binomial(n, P).
Weak priors (MAP): theta ~ N(0, 4^2), b ~ N(0, 4^2), log a ~ N(0, 0.5^2).

1. PT fit: item parameters and abilities from pretraining checkpoints only (p0 ... pend, 14 per seed).
2. Projection: with items fixed, the 1-D ability of every RL checkpoint (r1 ... r8, r12, r16) by MAP.
3. Residuals: for each RL examinee and item, observed vs predicted successes.  An item is **DIF+** (RL success beyond
   what moving along the pretraining ability axis predicts) if the one-sided binomial tail P(X >= c | n, p_pred) < 1e-3
   and the smoothed log-odds residual > ln 10.  "IRT-created" for (seed, RL ckpt) = DIF+ items that pend_s fails
   (0 / 512).
4. Fit comparison: deviance of RL examinees under the PT items vs under items refitted on all examinees, and a 2-D
   model on all examinees (does a second dimension load on RL?).
5. PT-step equivalent: theta along pretraining steps (log-linear fit over steps >= 3,000) extrapolated to RL abilities.
Writes capability_defs/analysis/out/irt_c<cap>.json.
"""
import argparse, json, math, os, sys
import numpy as np
from scipy.optimize import minimize
from scipy.special import expit, gammaln
from scipy.stats import binom

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cd_reads as R

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'out')
PT = [c for c in R.CKS if c.startswith('p')]
RL = [f'r{i}' for i in range(1, 9)] + ['r12', 'r16']
EXTRA = ['ctrl_pend_r8', 'ctrl_p5000_r8', 'ei_p5000_r8', 'ei_p1600_r8', 'cont_j7']


def load(cap, draws=(0, 1)):
    items = R.all_names()
    ex, C, N = [], [], []
    for s in R.SEEDS:
        for ck in PT + RL:
            c = np.zeros(len(items)); n = np.zeros(len(items)); have = False
            for x in draws:
                d = R.counts(cap, s, ck, x)
                if d is None:
                    continue
                for j, nm in enumerate(items):
                    if nm in d:
                        c[j] += d[nm][0]; n[j] += d[nm][1]; have = True
            if have:
                ex.append((s, ck)); C.append(c); N.append(n)
    if cap == 12:   # placebo / comparison examinees from rl-from-ckpt (compacted reads): replay-only controls and EI from earlier starts
        import gzip
        for s in R.SEEDS:
            for lab, stem in (('ctrl_pend_r8', f'c{s}_pend_r8'), ('ctrl_p5000_r8', f'c{s}_p5000_r8'),
                              ('ei_p5000_r8', f's{s}_p5000_r8'), ('ei_p1600_r8', f's{s}_p1600_r8')):
                c = np.zeros(len(items)); n = np.zeros(len(items)); have = False
                for x in draws:
                    for pool in R.POOLS:
                        f = f'{R.OA}/rl-from-ckpt/{stem}__{pool}_x{x}.jsonl.gz'
                        if not os.path.exists(f):
                            continue
                        for line in gzip.open(f, 'rt'):
                            r = json.loads(line); j = items.index(r['name'])
                            c[j] += r['n_ok']; n[j] += r['n_tried']; have = True
                if have:
                    ex.append((s, lab)); C.append(c); N.append(n)
        # J7: pend's pretraining continuation matched to the r8 ladder's GPU time (this run's reads, plain jsonl)
        root = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..')
        for s in R.SEEDS:
            c = np.zeros(len(items)); n = np.zeros(len(items)); have = False
            for x in draws:
                for pool in R.POOLS:
                    f = f'{root}/artifacts/cd/j7/s{s}_cont__{pool}_x{x}.jsonl'
                    if not os.path.exists(f):
                        continue
                    for line in open(f):
                        r = json.loads(line); j = items.index(r['name'])
                        c[j] += r['n_ok']; n[j] += r['n_tried']; have = True
            if have:
                ex.append((s, 'cont_j7')); C.append(c); N.append(n)
    return items, ex, np.array(C), np.array(N)


def nll_parts(theta, a, b, C, N):
    z = a[None, :] * (theta[:, None] - b[None, :])
    # log-likelihood of binomial counts (constant dropped), masked where N == 0
    ll = C * -np.logaddexp(0, -z) + (N - C) * -np.logaddexp(0, z)
    return ll


def fit(C, N, theta0=None, a0=None, b0=None, fix_items=False, iters=3000):
    M, I = C.shape
    th = np.zeros(M) if theta0 is None else theta0.copy()
    la = np.zeros(I) if a0 is None else np.log(a0)
    b = np.zeros(I) if b0 is None else b0.copy()
    if b0 is None:
        p = (C.sum(0) + 0.5) / (N.sum(0) + 1)
        b = -np.log(p / (1 - p)) / 2

    def unpack(v):
        if fix_items:
            return v, np.exp(la), b
        return v[:M], np.exp(v[M:M + I]), v[M + I:]

    def f(v):
        t, a, bb = unpack(v)
        z = a[None, :] * (t[:, None] - bb[None, :])
        s1 = expit(z)
        ll = (C * -np.logaddexp(0, -z) + (N - C) * -np.logaddexp(0, z)).sum()
        lp = -(t ** 2).sum() / (2 * 16)
        g_z = C - N * s1                       # d ll / d z
        gt = (g_z * a[None, :]).sum(1) - t / 16
        if fix_items:
            return -(ll + lp), -gt
        lp += -(bb ** 2).sum() / (2 * 16) - (np.log(a) ** 2).sum() / (2 * 0.25)
        ga = (g_z * (t[:, None] - bb[None, :])).sum(0) * a - np.log(a) / 0.25     # wrt log a
        gb = -(g_z * a[None, :]).sum(0) - bb / 16
        return -(ll + lp), -np.concatenate([gt, ga, gb])

    v0 = th if fix_items else np.concatenate([th, la, b])
    r = minimize(f, v0, jac=True, method='L-BFGS-B', options={'maxiter': iters})
    t, a, bb = unpack(r.x)
    return t, a, bb, r


def fit2d(C, N, iters=4000, seed=0):
    """z = a1_i t1_m + a2_i t2_m - d_i, MAP with N(0, 2^2) on loadings and abilities, N(0, 4^2) on d."""
    M, I = C.shape
    rng = np.random.default_rng(seed)
    v0 = np.concatenate([rng.normal(0, .1, 2 * M), rng.normal(0, .1, 2 * I), np.zeros(I)])

    def f(v):
        T = v[:2 * M].reshape(M, 2); A = v[2 * M:2 * M + 2 * I].reshape(I, 2); d = v[2 * M + 2 * I:]
        z = T @ A.T - d[None, :]
        s1 = expit(z)
        ll = (C * -np.logaddexp(0, -z) + (N - C) * -np.logaddexp(0, z)).sum()
        lp = -(T ** 2).sum() / 8 - (A ** 2).sum() / 8 - (d ** 2).sum() / 32
        g = C - N * s1
        gT = g @ A - T / 4; gA = g.T @ T - A / 4; gd = -g.sum(0) - d / 16
        return -(ll + lp), -np.concatenate([gT.ravel(), gA.ravel(), gd])

    r = minimize(f, v0, jac=True, method='L-BFGS-B', options={'maxiter': iters})
    v = r.x
    return v[:2 * M].reshape(M, 2), v[2 * M:2 * M + 2 * I].reshape(I, 2), v[2 * M + 2 * I:], r


def deviance(C, N, z):
    """binomial deviance vs the saturated model, summed."""
    p = expit(z); eps = 1e-12
    ph = np.where(N > 0, C / np.maximum(N, 1), 0)
    t1 = np.where(C > 0, C * (np.log(np.maximum(ph, eps)) - np.log(np.maximum(p, eps))), 0)
    t2 = np.where(N - C > 0, (N - C) * (np.log(np.maximum(1 - ph, eps)) - np.log(np.maximum(1 - p, eps))), 0)
    return 2 * (t1 + t2).sum()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--cap', type=int, default=12)
    ap.add_argument('--draw', default='01', help="'01' pooled (default), '0' or '1' one draw only (redraw floor)")
    a_ = ap.parse_args()
    os.makedirs(OUT, exist_ok=True)
    draws = tuple(int(c) for c in a_.draw)
    items, ex, C, N = load(a_.cap, draws)
    tag = f'c{a_.cap}' + ('' if a_.draw == '01' else f'_x{a_.draw}')
    is_pt = np.array([ck in PT for _, ck in ex])
    print(f'cap {a_.cap}: {len(ex)} examinees ({is_pt.sum()} pretraining), {len(items)} items, '
          f'{int(N.sum()):,} attempts, {int(C.sum()):,} successes')
    # 1. PT-only fit
    t_pt, a, b, r = fit(C[is_pt], N[is_pt])
    print(f'PT fit: converged={r.success} nit={r.nit}; a median {np.median(a):.2f} [{np.percentile(a, 10):.2f}, {np.percentile(a, 90):.2f}]')
    # 2. project RL checkpoints with items fixed
    rl_idx = np.where(~is_pt)[0]
    t_rl, _, _, r2 = fit(C[rl_idx], N[rl_idx], fix_items=True, a0=a, b0=b)
    theta = np.zeros(len(ex)); theta[is_pt] = t_pt; theta[rl_idx] = t_rl
    # centre the scale on the mean pend ability
    pend_mean = theta[[k for k, (s, ck) in enumerate(ex) if ck == 'pend']].mean()
    theta -= pend_mean; b = b - pend_mean
    print('\nability theta by checkpoint (pend mean = 0):')
    print('ckpt     ' + ' '.join(f'{"s" + str(s):>7s}' for s in R.SEEDS))
    tab = {}
    for ck in PT + RL + EXTRA:
        row = []
        for s in R.SEEDS:
            k = [j for j, e in enumerate(ex) if e == (s, ck)]
            row.append(theta[k[0]] if k else float('nan'))
        tab[ck] = row
        print(f'{ck:8s} ' + ' '.join(f'{v:7.2f}' for v in row))
    # 3. residuals / DIF for RL examinees
    z = a[None, :] * (theta[:, None] - b[None, :])
    p_pred = expit(z)
    out = {'cap': a_.cap, 'items': items, 'examinees': [list(e) for e in ex], 'theta': theta.tolist(),
           'a': a.tolist(), 'b': b.tolist(), 'dif': {}}
    pend_c = {s: C[[j for j, e in enumerate(ex) if e == (s, 'pend')][0]] for s in R.SEEDS}
    from scipy.stats import spearmanr
    print('\nQ8a: Spearman(predicted p from the PT-only 1-D model at the RL ability, observed p-hat), per seed:')
    for ck in ('r8', 'r16'):
        vals = []
        for s in R.SEEDS:
            k = [j for j, e in enumerate(ex) if e == (s, ck)]
            if k:
                j = k[0]; m = N[j] > 0
                vals.append(spearmanr(p_pred[j][m], (C[j] / np.maximum(N[j], 1))[m]).correlation)
        print(f'  {ck}: ' + ' '.join(f'{v:.3f}' for v in vals))
    out['spearman'] = {}
    print('\nDIF+ items per RL examinee (tail p < 1e-3 and log-odds residual > ln 10); "created" = DIF+ and pend 0/512:')
    for j in rl_idx:
        s, ck = ex[j]
        c, n, pp = C[j], N[j], p_pred[j]
        tail = binom.sf(c - 1, n.astype(int), pp)                  # P(X >= c)
        lo_obs = np.log((c + .5) / (n - c + .5)); lo_pred = np.log(pp / (1 - pp))
        res = lo_obs - lo_pred
        difp = np.where((n > 0) & (tail < 1e-3) & (res > math.log(10)))[0]
        difm = np.where((n > 0) & (binom.cdf(c, n.astype(int), pp) < 1e-3) & (res < -math.log(10)))[0]
        created = [items[i] for i in difp if pend_c[s][i] == 0]
        out['dif'][f's{s}_{ck}'] = {'dif_plus': [items[i] for i in difp], 'dif_minus': [items[i] for i in difm],
                                   'created': created, 'resid': res.round(3).tolist()}
        if ck in ('r8', 'r16', 'r4', 'r12') or ck in EXTRA:
            print(f'  s{s} {ck:13s}: theta {theta[j]:5.2f}  DIF+ {len(difp):3d}  DIF- {len(difm):3d}  created {len(created):3d}')
        if (s, ck) == (1, 'r16'):
            lem6 = ['la_transfer_478', 'la_transfer_1572', 'la_transfer_956', 'la_transfer_795', 'la_transfer_1453', 'la_transfer_1424']
            order = np.argsort(-np.where(n > 0, res, -1e9)); top = set(order[:max(1, int(0.1 * (n > 0).sum()))])
            hit = [nm for nm in lem6 if items.index(nm) in top]
            print(f'  Q8c: s1 r16 top-decile positive residuals contain {len(hit)} of the 6 holdout250 A v ~A instances: {hit}')
            out['q8c'] = hit
    # 4. fit comparison
    dev_rl_pt = deviance(C[rl_idx], N[rl_idx], z[rl_idx])
    t_all, a_all, b_all, r3 = fit(C, N)
    z_all = a_all[None, :] * (t_all[:, None] - b_all[None, :])
    dev_rl_all = deviance(C[rl_idx], N[rl_idx], z_all[rl_idx])
    dev_pt_pt = deviance(C[is_pt], N[is_pt], z[is_pt]); dev_pt_all = deviance(C[is_pt], N[is_pt], z_all[is_pt])
    n_obs_rl = int((N[rl_idx] > 0).sum()); n_obs_pt = int((N[is_pt] > 0).sum())
    print(f'\ndeviance per (examinee, item) cell: PT cells under PT items {dev_pt_pt / n_obs_pt:.2f}, under all-fit items {dev_pt_all / n_obs_pt:.2f}; '
          f'RL cells under PT items {dev_rl_pt / n_obs_rl:.2f}, under all-fit items {dev_rl_all / n_obs_rl:.2f}')
    T2, A2, d2, r4 = fit2d(C, N)
    z2 = T2 @ A2.T - d2[None, :]
    dev2_rl = deviance(C[rl_idx], N[rl_idx], z2[rl_idx]); dev2_pt = deviance(C[is_pt], N[is_pt], z2[is_pt])
    print(f'2-D fit (all examinees): deviance per cell PT {dev2_pt / n_obs_pt:.2f}, RL {dev2_rl / n_obs_rl:.2f}')
    # rotate so dim 1 = direction of PT progress (pend - p1600 mean), dim 2 orthogonal
    def mean_of(ck):
        return T2[[j for j, e in enumerate(ex) if e[1] == ck]].mean(0)
    u = mean_of('pend') - mean_of('p1600'); u /= np.linalg.norm(u); w = np.array([-u[1], u[0]])
    proj = {ck: (float(mean_of(ck) @ u), float(mean_of(ck) @ w)) for ck in ('p1600', 'p5000', 'p12000', 'pend', 'r1', 'r4', 'r8', 'r12', 'r16') if any(e[1] == ck for e in ex)}
    print('2-D abilities (mean over seeds) on the PT-progress axis u and the orthogonal axis w:')
    for ck, (pu, pw) in proj.items():
        print(f'  {ck:7s} u {pu:7.2f}  w {pw:7.2f}')
    out['fitcmp'] = {'dev_cell_pt_ptitems': dev_pt_pt / n_obs_pt, 'dev_cell_pt_allitems': dev_pt_all / n_obs_pt,
                     'dev_cell_rl_ptitems': dev_rl_pt / n_obs_rl, 'dev_cell_rl_allitems': dev_rl_all / n_obs_rl,
                     'dev_cell_2d_pt': dev2_pt / n_obs_pt, 'dev_cell_2d_rl': dev2_rl / n_obs_rl, 'proj2d': proj}
    # 5. PT-step equivalent: theta vs log(step) over steps >= 3000, extrapolate
    print('\nPT-step equivalent (theta = alpha + beta ln step, fitted per seed on steps 3,000 ... 20,000 and pend at its'
          ' recorded step count):')
    steps_end = {0: 24077, 1: 24345, 2: 24328}       # trajectory's Stage-1 step counts (run summary)
    out['pt_equiv'] = {}
    for s in R.SEEDS:
        xs, ys = [], []
        for ck in ('p3000', 'p5000', 'p8000', 'p12000', 'p16000', 'p20000', 'pend'):
            st = R.PT_STEPS.get(ck, steps_end[s])
            xs.append(math.log(st)); ys.append(tab[ck][s])
        beta, alpha = np.polyfit(xs, ys, 1)
        eq = {}
        for ck in ('r1', 'r4', 'r8', 'r12', 'r16'):
            th = tab[ck][s]
            if not math.isnan(th):
                eq[ck] = math.exp((th - alpha) / beta) / steps_end[s] if beta > 0 else float('inf')
        out['pt_equiv'][s] = {'alpha': alpha, 'beta': beta, 'multiplier': eq}
        print(f'  s{s}: slope {beta:.3f} per e-fold of steps; RL ability = PT length x ' +
              ', '.join(f'{k} {v:,.1f}' for k, v in eq.items()))
    json.dump(out, open(f'{OUT}/irt_{tag}.json', 'w'))


if __name__ == '__main__':
    main()
