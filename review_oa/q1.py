"""Reviewer Q1 recount: own feature table + own CV (pre-registration Q1)."""
import json, hashlib, math, sys, collections
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.metrics import roc_auc_score
import rvc
X_ = int(sys.argv[1]) if len(sys.argv) > 1 else 0
REF = {d['name']: d for d in map(json.loads, open('rv/ref_targets.jsonl'))}
PEND = {('c12',0):24077,('c12',1):24345,('c12',2):24328,('c6',0):24511,('c6',1):24120,('c6',2):24113}
def stepn(ck, run, s): return PEND[(run, s)] if ck == 'pend' else int(ck[1:])
def feats(run, seed, ck, name):
    """features of the reference proof under checkpoint ck (c12/c6 score files; rfc starts are c12 p<X>)."""
    srun = 'c12' if run == 'rfc' else run
    t = 'ref:' + name
    s = rvc.score(srun, seed, ck)[t]; lp = s['step_lp']; m = rvc.tmeta(srun, seed)[t]
    o = sorted(lp); i = int(np.argmin(lp))
    w = [rvc.score(srun, seed, c)[t]['w1'] for c in prev3(ck)]
    xs = [math.log10(stepn(c, srun, seed)) for c in prev3(ck)]
    slope = np.polyfit(xs, [min(rvc.score(srun, seed, c)[t]['step_lp']) for c in prev3(ck)], 1)[0]
    return dict(w1=o[0], w2=o[1] if len(o) > 1 else 0.0, w3=o[2] if len(o) > 2 else 0.0, n4=sum(x < -4 for x in lp),
                n8=sum(x < -8 for x in lp), tot=sum(lp), lines=REF[name]['proof'].count(' : '), ts=m['term_size'],
                na=len(lp), slope=slope, kind=rvc.cls(m['actions_b0'][i]), w1chk=s['w1'])
def prev3(ck):
    j = rvc.PT.index(ck); return rvc.PT[j-2:j+1]
rows = []
for run, starts in (('c12', ['pend']), ('c6', ['pend']), ('rfc', rvc.STARTS)):
    for seed in range(3):
        for st in starts:
            if run == 'rfc':
                s0 = rvc.solved('c12', f's{seed}_{st}', X_); s8 = rvc.solved('rfc', f's{seed}_{st}_r8', X_)
            else:
                s0 = rvc.solved(run, f's{seed}_pend', X_); s8 = rvc.solved(run, f's{seed}_r8', X_)
            for name in REF:
                if name in s0: continue
                f = feats(run, seed, st, name); f.update(run=run, seed=seed, start=st, name=name, y=int(name in s8))
                rows.append(f)
assert all(abs(r['w1'] - r['w1chk']) < 1e-3 for r in rows)
KINDS = sorted({r['kind'] for r in rows})
NUM = ['w1','w2','w3','n4','n8','tot','lines','ts','na','slope']
def X(rs, w1only=False):
    if w1only: return np.array([[r['w1']] for r in rs])
    return np.array([[r[k] for k in NUM] + [r['kind'] == c for c in KINDS] for r in rs], float)
def fit(kind, tr, te):
    y = np.array([r['y'] for r in tr])
    if kind == 'gbm':
        m = HistGradientBoostingClassifier(max_depth=3, max_iter=100, learning_rate=0.1, random_state=0).fit(X(tr), y)
        return m.predict_proba(X(te))[:, 1]
    A, B = X(tr, kind == 'w1'), X(te, kind == 'w1'); mu, sd = A.mean(0), A.std(0); sd[sd == 0] = 1
    m = LogisticRegression(C=1.0, max_iter=5000).fit((A - mu) / sd, y)
    return m.predict_proba((B - mu) / sd)[:, 1]
def fold(n): return int(hashlib.sha1(n.encode()).hexdigest(), 16) % 5   # own hash (differs from executor's md5)
def cv(rs):
    P = {k: np.full(len(rs), np.nan) for k in ('w1', 'logit', 'gbm')}
    for s in range(3):
        for f in range(5):
            te = [i for i, r in enumerate(rs) if r['seed'] == s and fold(r['name']) == f]
            tr = [r for r in rs if r['seed'] != s and fold(r['name']) != f]
            for k in P: P[k][te] = fit(k, tr, [rs[i] for i in te])
    return P
def boot(rs, P, B=1000):
    rng = np.random.default_rng(7); names = sorted({r['name'] for r in rs}); ix = collections.defaultdict(list)
    for i, r in enumerate(rs): ix[r['name']].append(i)
    y = np.array([r['y'] for r in rs]); out = collections.defaultdict(list)
    for _ in range(B):
        ii = np.concatenate([ix[names[j]] for j in rng.integers(0, len(names), len(names))])
        if 0 < y[ii].sum() < len(ii):
            a = {k: roc_auc_score(y[ii], P[k][ii]) for k in P}
            for k in a: out[k].append(a[k])
            out['logit-w1'].append(a['logit'] - a['w1']); out['gbm-logit'].append(a['gbm'] - a['logit'])
    return {k: [round(float(np.percentile(v, 2.5)), 3), round(float(np.percentile(v, 97.5)), 3)] for k, v in out.items()}
def x50(rs):
    A = np.array([r['w1'] for r in rs])[:, None]; y = np.array([r['y'] for r in rs])
    m = LogisticRegression(C=1.0, max_iter=5000).fit((A - A.mean()) / A.std(), y)
    return float(A.mean() - m.intercept_[0] * A.std() / m.coef_[0][0])
res = {'x': X_, 'n': {}}
for run in ('c12', 'c6'):
    rs = [r for r in rows if r['run'] == run]; y = np.array([r['y'] for r in rs]); P = cv(rs)
    auc = {k: round(roc_auc_score(y, p), 3) for k, p in P.items()}
    ps = {k: [round(roc_auc_score(y[[r['seed'] == s for r in rs]], p[[r['seed'] == s for r in rs]]), 3) for s in range(3)] for k, p in P.items()}
    # standardised logistic coefficients on all rows
    A = X(rs); mu, sd = A.mean(0), A.std(0); sd[sd == 0] = 1
    m = LogisticRegression(C=1.0, max_iter=5000).fit((A - mu) / sd, y)
    coef = dict(sorted(zip(NUM + ['k=' + k for k in KINDS], m.coef_[0].round(3)), key=lambda kv: -abs(kv[1]))[:6])
    # threshold-only baseline: best single cut on w1 (in-sample, optimistic) -> AUC of a step function
    res[run] = dict(n=len(rs), pos=int(y.sum()), per_seed_n=[sum(r['seed'] == s for r in rs) for s in range(3)],
                    per_seed_pos=[sum(r['y'] for r in rs if r['seed'] == s) for s in range(3)], auc=auc, auc_seed=ps,
                    ci=boot(rs, P), x50=round(x50(rs), 2), x50_seed=[round(x50([r for r in rs if r['seed'] == s]), 2) for s in range(3)],
                    coef=coef, kinds_of_worst=collections.Counter(r['kind'] for r in rs).most_common())
    print(run, json.dumps(res[run]), flush=True)
# transfer: train on all of one run, test on the other / rfc starts (raw AUC; w1-only and logit and gbm)
def tr_te(tr, te):
    y = np.array([r['y'] for r in te]); return {k: round(roc_auc_score(y, fit(k, tr, te)), 3) for k in ('w1', 'logit', 'gbm')}
c12 = [r for r in rows if r['run'] == 'c12']; c6 = [r for r in rows if r['run'] == 'c6']
res['c12->c6'] = tr_te(c12, c6); res['c6->c12'] = tr_te(c6, c12)
for st in rvc.STARTS:
    te = [r for r in rows if r['run'] == 'rfc' and r['start'] == st]; y = [r['y'] for r in te]
    res['c12->rfc_' + st] = dict(tr_te(c12, te), n=len(te), pos=sum(y), x50_own=round(x50(te), 2),
                                  w1_auc_raw=round(roc_auc_score(y, [r['w1'] for r in te]), 3))
    print(st, res['c12->rfc_' + st], flush=True)
print('transfer', res['c12->c6'], res['c6->c12'])
json.dump(res, open(f'rv/q1_x{X_}.json', 'w'), indent=1, default=str)
json.dump(rows, open(f'rv/q1_rows_x{X_}.json', 'w'), default=float)
# theorem-fold-disjoint transfer (train folds != f on source, test fold f on target) + GBM permutation importance
def tr_te_disj(src, dst):
    P = {k: np.full(len(dst), np.nan) for k in ('w1', 'logit', 'gbm')}
    for f in range(5):
        te = [i for i, r in enumerate(dst) if fold(r['name']) == f]; tr = [r for r in src if fold(r['name']) != f]
        for k in P: P[k][te] = fit(k, tr, [dst[i] for i in te])
    y = np.array([r['y'] for r in dst]); return {k: round(roc_auc_score(y, p), 3) for k, p in P.items()}
res['disj'] = {'c12->c6': tr_te_disj(c12, c6), 'c6->c12': tr_te_disj(c6, c12)}
for st in rvc.STARTS: res['disj']['c12->' + st] = tr_te_disj(c12, [r for r in rows if r['run'] == 'rfc' and r['start'] == st])
print('disjoint transfer', res['disj'])
rng = np.random.default_rng(3); FE = NUM + ['kind']
for run, rs in (('c12', c12), ('c6', c6)):
    imp = collections.defaultdict(list)
    for s in range(3):
        for f in range(5):
            te = [r for r in rs if r['seed'] == s and fold(r['name']) == f]; tr = [r for r in rs if r['seed'] != s and fold(r['name']) != f]
            yt = np.array([r['y'] for r in te])
            if len(set(yt)) < 2: continue
            m = HistGradientBoostingClassifier(max_depth=3, max_iter=100, learning_rate=0.1, random_state=0).fit(X(tr), [r['y'] for r in tr])
            a0 = roc_auc_score(yt, m.predict_proba(X(te))[:, 1])
            for k in FE:
                vals = [r[k] for r in te]; d = []
                for _ in range(10):
                    pv = rng.permutation(len(te)); te2 = [dict(r, **{k: vals[pv[i]]}) for i, r in enumerate(te)]
                    d.append(a0 - roc_auc_score(yt, m.predict_proba(X(te2))[:, 1]))
                imp[k].append(np.mean(d))
    res['perm_' + run] = dict(sorted({k: round(float(np.mean(v)), 3) for k, v in imp.items()}.items(), key=lambda kv: -kv[1]))
    print('perm', run, res['perm_' + run])
json.dump(res, open(f'rv/q1_x{X_}.json', 'w'), indent=1, default=str)
