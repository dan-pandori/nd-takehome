#!/usr/bin/env python3
"""organism-analysis Q1: which start-of-RL features predict "solved at r8" (preregistration Q1).

Input data/oa/q1_rows.jsonl (oa_q1_table.py).  Population: rows the start's x0 read does not solve (primary;
--x 1 for the x1 robustness check).  Models (fixed hyper-parameters): logistic (standardised, L2, C 1), w1-only
logistic, HistGradientBoosting (depth 3, 100 iterations, lr 0.1).  CV: within run, folds = held-out seed x held-out
theorem fold (5 hash folds), no seed or theorem in both train and test; across caps (c12 <-> c6) and starts
(c12 pend -> rfc starts), theorem-fold disjoint.  Writes artifacts/oa/q1_results.json; prints the tables.
"""
import argparse, hashlib, json, math, os, sys
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.metrics import roc_auc_score, log_loss, brier_score_loss
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from oa_common import CLASSES

NUM = ['w1', 'w2', 'w3', 'n_lt4', 'n_lt8', 'total', 'nd_lines', 'term_size', 'n_actions', 'slope']
KCLS = [c for c in CLASSES if c != 'exact']           # the worst step is never `exact` here; one-hot of the rest
FEATS = NUM + ['cls=' + c for c in KCLS]
NB = 1000


def tfold(name, k=5):
    return int(hashlib.md5(name.encode()).hexdigest(), 16) % k


def X_of(rows, med=None):
    X = np.array([[np.nan if r[f] is None else float(r[f]) for f in NUM] + [float(r['w1_class'] == c) for c in KCLS]
                  for r in rows])
    return X


def fit_predict(kind, Xtr, ytr, Xte):
    if kind == 'w1':
        Xtr, Xte = Xtr[:, :1], Xte[:, :1]
    if kind in ('logit', 'w1'):
        med = np.nanmedian(Xtr, 0)
        Xtr = np.where(np.isnan(Xtr), med, Xtr); Xte = np.where(np.isnan(Xte), med, Xte)
        mu, sd = Xtr.mean(0), Xtr.std(0); sd[sd == 0] = 1
        m = LogisticRegression(C=1.0, max_iter=2000).fit((Xtr - mu) / sd, ytr)
        return m.predict_proba((Xte - mu) / sd)[:, 1], (m, mu, sd)
    m = HistGradientBoostingClassifier(max_depth=3, max_iter=100, learning_rate=0.1, random_state=0).fit(Xtr, ytr)
    return m.predict_proba(Xte)[:, 1], m


def metrics(y, p):
    p = np.clip(p, 1e-6, 1 - 1e-6)
    return {'auc': roc_auc_score(y, p) if 0 < y.sum() < len(y) else None, 'logloss': log_loss(y, p, labels=[0, 1]),
            'brier': brier_score_loss(y, p)}


def boot_auc(names, y, preds, B=NB, seed=0):
    """theorem-resampling bootstrap: {model: [lo, hi]} and paired differences vs 'w1'."""
    rng = np.random.default_rng(seed)
    un = sorted(set(names)); idx = {n: [] for n in un}
    for i, n in enumerate(names):
        idx[n].append(i)
    out = {k: [] for k in preds}
    diff = {k: [] for k in preds if k != 'w1'}
    for _ in range(B):
        ii = np.concatenate([idx[un[j]] for j in rng.integers(0, len(un), len(un))])
        if not 0 < y[ii].sum() < len(ii):
            continue
        a = {k: roc_auc_score(y[ii], p[ii]) for k, p in preds.items()}
        for k in a:
            out[k].append(a[k])
        for k in diff:
            diff[k].append(a[k] - a['w1'])
    q = lambda v: [round(float(np.percentile(v, 2.5)), 3), round(float(np.percentile(v, 97.5)), 3)]
    return {k: q(v) for k, v in out.items()}, {k: q(v) for k, v in diff.items()}


def within(rows, label):
    """seed x theorem-fold CV inside one group of rows."""
    seeds = sorted({r['seed'] for r in rows})
    y = np.array([r['y'] for r in rows]); X = X_of(rows)
    preds = {k: np.full(len(rows), np.nan) for k in ('w1', 'logit', 'gbm')}
    perm = {f: [] for f in FEATS}
    for s in seeds:
        for f in range(5):
            te = [i for i, r in enumerate(rows) if r['seed'] == s and tfold(r['name']) == f]
            tr = [i for i, r in enumerate(rows) if r['seed'] != s and tfold(r['name']) != f]
            if not te or len(set(y[tr])) < 2:
                continue
            for k in preds:
                preds[k][te] = fit_predict(k, X[tr], y[tr], X[te])[0]
    ok = ~np.isnan(preds['logit'])
    names = [r['name'] for i, r in enumerate(rows) if ok[i]]
    P = {k: v[ok] for k, v in preds.items()}
    res = {'label': label, 'n': int(ok.sum()), 'pos_rate': round(float(y[ok].mean()), 3)}
    res['metrics'] = {k: {m: (round(v, 4) if v is not None else None) for m, v in metrics(y[ok], p).items()} for k, p in P.items()}
    res['auc_ci'], res['auc_diff_vs_w1_ci'] = boot_auc(names, y[ok], P)
    sd = np.array([r['seed'] for i, r in enumerate(rows) if ok[i]])
    res['auc_per_seed'] = {k: [round(roc_auc_score(y[ok][sd == s], p[sd == s]), 3) if 0 < y[ok][sd == s].sum() < (sd == s).sum() else None
                               for s in seeds] for k, p in P.items()}
    for k in ('w1', 'logit', 'gbm'):
        v = [a for a in res['auc_per_seed'][k] if a is not None]
        res.setdefault('auc_seed_sd', {})[k] = round(float(np.std(v, ddof=1)), 3) if len(v) > 1 else None
    # importance: standardised logistic coefficients on all rows; GBM permutation importance on held-out folds
    _, (m, mu, sd_) = fit_predict('logit', X, y, X[:2])
    res['logit_coef'] = {f: round(float(c), 3) for f, c in zip(FEATS, m.coef_[0])}
    _, (m1, mu1, sd1) = fit_predict('w1', X, y, X[:2])
    b0, b1 = float(m1.intercept_[0]), float(m1.coef_[0][0]) / sd1[0]
    res['w1_x50'] = round(float(mu1[0] - b0 / b1), 2)          # w1 where the w1-only model gives 0.5
    res['w1_slope_per_nat'] = round(b1, 3)
    rng = np.random.default_rng(1)
    base = roc_auc_score(y[ok], P['gbm'])
    Xok = X[ok]
    # permutation importance of the held-out GBM predictions needs the fitted fold models: refit per fold
    imp = {f: [] for f in FEATS}
    for s in seeds:
        for fo in range(5):
            te = [i for i, r in enumerate(rows) if r['seed'] == s and tfold(r['name']) == fo]
            tr = [i for i, r in enumerate(rows) if r['seed'] != s and tfold(r['name']) != fo]
            if not te or len(set(y[tr])) < 2 or len(set(y[te])) < 2:
                continue
            _, g = fit_predict('gbm', X[tr], y[tr], X[te])
            a0 = roc_auc_score(y[te], g.predict_proba(X[te])[:, 1])
            for j, f in enumerate(FEATS):
                Xp = X[te].copy(); Xp[:, j] = rng.permutation(Xp[:, j])
                imp[f].append(a0 - roc_auc_score(y[te], g.predict_proba(Xp)[:, 1]))
    res['gbm_perm_importance'] = {f: round(float(np.mean(v)), 4) for f, v in imp.items() if v}
    return res


def transfer(train, test, label):
    """train on one group, test on another, theorem-fold disjoint (train folds != f, test fold f)."""
    yt = np.array([r['y'] for r in test]); Xtr_all = X_of(train); ytr_all = np.array([r['y'] for r in train]); Xte = X_of(test)
    P = {k: np.full(len(test), np.nan) for k in ('w1', 'logit', 'gbm')}
    for f in range(5):
        te = [i for i, r in enumerate(test) if tfold(r['name']) == f]
        tr = [i for i, r in enumerate(train) if tfold(r['name']) != f]
        for k in P:
            P[k][te] = fit_predict(k, Xtr_all[tr], ytr_all[tr], Xte[te])[0]
    res = {'label': label, 'n_train': len(train), 'n_test': len(test), 'pos_rate_test': round(float(yt.mean()), 3)}
    res['metrics'] = {k: {m: (round(v, 4) if v is not None else None) for m, v in metrics(yt, p).items()} for k, p in P.items()}
    res['auc_ci'], res['auc_diff_vs_w1_ci'] = boot_auc([r['name'] for r in test], yt, P)
    res['mean_pred'] = {k: round(float(p.mean()), 3) for k, p in P.items()}
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--x', type=int, default=0, help='sample seed defining start-unsolved and r8-solved')
    ap.add_argument('--out', default='artifacts/oa/q1_results.json')
    a = ap.parse_args()
    rows = [json.loads(l) for l in open('data/oa/q1_rows.jsonl')]
    pop = []
    for r in rows:
        if r[f'ok0_x{a.x}'] == 0:
            r['y'] = int(r[f'ok8_x{a.x}'] > 0); pop.append(r)
    G = lambda run, start=None: [r for r in pop if r['run'] == run and (start is None or r['start'] == start)]
    out = {'x': a.x, 'within': [], 'transfer': []}
    for lab, g in [('c12 pend', G('c12')), ('c6 pend', G('c6')), ('rfc pooled', G('rfc'))] + \
                  [(f'rfc {s}', G('rfc', s)) for s in ('p1600', 'p5000', 'p12000', 'p16000')]:
        out['within'].append(within(g, lab))
    out['transfer'].append(transfer(G('c12'), G('c6'), 'c12 pend -> c6 pend'))
    out['transfer'].append(transfer(G('c6'), G('c12'), 'c6 pend -> c12 pend'))
    for s in ('p1600', 'p5000', 'p12000', 'p16000'):
        out['transfer'].append(transfer(G('c12'), G('rfc', s), f'c12 pend -> rfc {s}'))
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    json.dump(out, open(a.out, 'w'), indent=1)
    print(f'Q1 (x{a.x}): population = start-unsolved; target = solved at r8.  AUC [95 % theorem bootstrap]')
    print(f"{'group':<14}{'n':>5}{'pos':>6}  {'w1-only':<20}{'logistic':<20}{'GBM':<20}{'logit-w1 diff CI':<18}{'x50':>7}  per-seed AUC (w1 / logit / gbm), seed SD")
    for r in out['within']:
        m = r['metrics']; c = r['auc_ci']
        cell = lambda k: f"{m[k]['auc']:.3f} [{c[k][0]:.2f},{c[k][1]:.2f}]"
        print(f"{r['label']:<14}{r['n']:>5}{r['pos_rate']:>6}  {cell('w1'):<20}{cell('logit'):<20}{cell('gbm'):<20}"
              f"{str(r['auc_diff_vs_w1_ci']['logit']):<18}{r['w1_x50']:>7}  {r['auc_per_seed']['w1']} / {r['auc_per_seed']['logit']} / {r['auc_per_seed']['gbm']}, {r['auc_seed_sd']}")
    print('\ntransfer (theorem-fold disjoint):')
    for r in out['transfer']:
        m = r['metrics']; c = r['auc_ci']
        print(f"{r['label']:<24} n {r['n_test']:>4} pos {r['pos_rate_test']}  " + '  '.join(
            f"{k} {m[k]['auc']:.3f} [{c[k][0]:.2f},{c[k][1]:.2f}] ll {m[k]['logloss']:.3f} meanp {r['mean_pred'][k]}" for k in ('w1', 'logit', 'gbm')))
    print('\nstandardised logistic coefficients / GBM permutation importance (AUC drop):')
    for r in out['within'][:3]:
        top = sorted(r['logit_coef'].items(), key=lambda kv: -abs(kv[1]))[:6]
        imp = sorted(r['gbm_perm_importance'].items(), key=lambda kv: -kv[1])[:6]
        print(f"  {r['label']}: coef {top}\n  {'':<{len(r['label'])}}  perm {imp}")


if __name__ == '__main__':
    main()
