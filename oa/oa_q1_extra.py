#!/usr/bin/env python3
"""organism-analysis Q1 supplement: univariate AUC of each feature (raw value; > 0.5 = higher value -> more often
solved at r8), CV AUC of the two-feature logistic (w1, term_size), and P(solved at r8) by term size and by w1 bin.
Same population / folds as oa_q1_models.py (x0)."""
import json, os, sys
import numpy as np
from sklearn.metrics import roc_auc_score
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import oa_q1_models as M

rows = [json.loads(l) for l in open('data/oa/q1_rows.jsonl')]
pop = [dict(r, y=int(r['ok8_x0'] > 0)) for r in rows if r['ok0_x0'] == 0]
groups = [('c12 pend', [r for r in pop if r['run'] == 'c12']), ('c6 pend', [r for r in pop if r['run'] == 'c6']),
          ('rfc pooled', [r for r in pop if r['run'] == 'rfc'])]
out = {}
print('univariate AUC (raw feature value):')
print(f"{'group':<12}" + ''.join(f'{f:>10}' for f in M.NUM))
for lab, g in groups:
    y = np.array([r['y'] for r in g])
    a = {}
    for f in M.NUM:
        ok = [i for i, r in enumerate(g) if r[f] is not None]
        a[f] = round(roc_auc_score(y[ok], [g[i][f] for i in ok]), 3)
    out.setdefault('univariate', {})[lab] = a
    print(f'{lab:<12}' + ''.join(f'{a[f]:>10}' for f in M.NUM))
# two-feature logistic, same CV
keep = [M.NUM.index('w1'), M.NUM.index('term_size')]
print('\nCV AUC, logistic on (w1, term_size) and on term_size alone:')
for lab, g in groups:
    y = np.array([r['y'] for r in g]); X = M.X_of(g)
    for name, cols in (('w1+term', keep), ('term', [keep[1]])):
        p = np.full(len(g), np.nan)
        for s in (0, 1, 2):
            for f in range(5):
                te = [i for i, r in enumerate(g) if r['seed'] == s and M.tfold(r['name']) == f]
                tr = [i for i, r in enumerate(g) if r['seed'] != s and M.tfold(r['name']) != f]
                if te:
                    Xa = X[:, cols]
                    p[te] = M.fit_predict('logit', Xa[tr], y[tr], Xa[te])[0]
        ok = ~np.isnan(p)
        ci, _ = M.boot_auc([g[i]['name'] for i in np.where(ok)[0]], y[ok], {'w1': p[ok]})
        out.setdefault('cv2', {})[f'{lab}|{name}'] = [round(roc_auc_score(y[ok], p[ok]), 3), ci['w1']]
        print(f'  {lab:<12} {name:<8} {roc_auc_score(y[ok], p[ok]):.3f} {ci["w1"]}')
print('\nP(solved at r8 | term size) [n]:')
for lab, g in groups:
    t = {}
    for r in g:
        k = min(r['term_size'], 9)
        t.setdefault(k, []).append(r['y'])
    out.setdefault('by_term', {})[lab] = {k: [round(float(np.mean(v)), 2), len(v)] for k, v in sorted(t.items())}
    print(f'  {lab:<12}', '  '.join(f'{k}{"+" if k == 9 else ""}: {np.mean(v):.2f} [{len(v)}]' for k, v in sorted(t.items())))
print('\nP(solved at r8 | w1 bin) [n]:')
bins = [-1e9, -30, -20, -15, -12, -9, -6, -4, 1]
for lab, g in groups:
    t = {}
    for r in g:
        b = max(i for i in range(len(bins) - 1) if r['w1'] >= bins[i])
        t.setdefault(b, []).append(r['y'])
    out.setdefault('by_w1', {})[lab] = {f'{bins[k]}..{bins[k+1]}': [round(float(np.mean(v)), 2), len(v)] for k, v in sorted(t.items())}
    print(f'  {lab:<12}', '  '.join(f'[{bins[k]},{bins[k+1]}): {np.mean(v):.2f} [{len(v)}]' for k, v in sorted(t.items())))
json.dump(out, open('artifacts/oa/q1_extra.json', 'w'), indent=1)

# ---- post hoc (not pre-registered): is term size a proxy for "the reference needs reductio"? ----
from oa_load import targets_meta
from oa_common import step_class
print('\nPOST HOC: P(solved at r8) by whether the reference uses Classical.byContradiction, x term size <= 8 / >= 9 [n]:')
for lab, g in groups:
    t = {}
    for r in g:
        m = targets_meta('c12', 0)['ref:' + r['name']]
        bc = any(step_class(a) == 'box:bycontra' for a in m['actions_b0'])
        r['bycontra'] = int(bc)
        t.setdefault((bc, r['term_size'] >= 9), []).append(r['y'])
    out.setdefault('posthoc_bycontra', {})[lab] = {f'bycontra={k[0]},term>=9={k[1]}': [round(float(np.mean(v)), 2), len(v)] for k, v in sorted(t.items())}
    print(f'  {lab:<12}', '  '.join(f'bc={int(k[0])} t9+={int(k[1])}: {np.mean(v):.2f} [{len(v)}]' for k, v in sorted(t.items())))
    y = np.array([r['y'] for r in g])
    print(f'  {"":<12} univariate AUC of uses-reductio: {roc_auc_score(y, [-r["bycontra"] for r in g]):.3f}  (oriented: reductio -> less often solved)')
json.dump(out, open('artifacts/oa/q1_extra.json', 'w'), indent=1)
