#!/usr/bin/env python3
"""Q4: which measure predicts where kalmar-pretrain's models fail?  (run kalmar-complexity)

  .venv-tok/bin/python kalmar_complexity/q4_analysis.py   # -> artifacts/kc/q4/q4_results.json + tables on stdout

Outcome: teacher-forced error (1 - agreement) per step type on tf1200 (kalmar-pretrain's stored verdicts, joined by
q4_join.py), KAL-D s0 / s1 / s2 and their mean; robustness: KAL-D+A, KAL-C, and the per-type code length (B1-snap).
Step types: the builder's tags with `close:*` grouped (the review's E1 grouping), those with >= 500 states.

Predictors per step type (each a mean over the type's tf1200 states unless stated):
  py_bytes, py_tokens   bytes / Qwen3 tokens of the code in ksl_alg.py that emits the step (snippets below)
  blc_bits              BLC bits of the term that emits the step (kalmar_complexity/programs/blc, if available)
  rasp_ops, rasp_depth  RASP-L ops / attention depth on the step's decision path (programs/rasp, if available)
  tree_path             tests on the decision-tree path to the state's template (artifacts/kc/dtree/tree_u_b3.json)
  explored, focus_h, target_h, decl_len, act_len, ref_dist, depth, state_len   q4_states.py's demand measures
  log2_ops              log2(1 + policy.py's operations for the state): Levin's Kt minus the (constant) program length
  log_freq              log10 of the type's pairs in K12-Kalmár (artifacts/kc/tokens_kal_sl.json): a data baseline
  b2_bits_L/M/S         B2 code per loss token of the type, summed over blocks (if available)
Test: Spearman rho across types, two-sided permutation p (100,000 permutations), per seed and for the seed mean;
partial Spearman given log frequency (ranks residualised on the frequency rank; 20,000 permutations).
State level: logistic regression of error on step type (dummies) +/- the standardised demand measures, per seed;
likelihood-ratio test (chi-square, df = number of demand measures).
"""
import collections, gzip, json, math, os, sys
import numpy as np
from scipy import stats

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
A = lambda p: os.path.join(ROOT, p)
SNIP = {
    'pr': "Q=[E(p,'PR')for p in P]",
    'lem': "def M(x):",                                     # the whole of M (all excluded-middle steps)
    'split': "if A:x=A[0];return E(G,'ORE',[W[x]],[X(x,lambda h:D(A[1:],{**v,x:1})),X((N,x),lambda h:D(A[1:],{**v,x:0}))])",
    'efq': "for p,l in zip(P,Q):\n   if not V(p,v):f=E(F,'NEGE',[l,I(p,v)]);return f if G==F else E(G,'BOTE',[f])",
    'close': "def X(h,y):",                                 # the whole of X (opening / closing boxes)
    'end': "return T",
    'leaf:bot-': "if f==F:return J(X(F,lambda h:0))",
    'leaf:not+': "  if N==k:\n   a=I(f[1],v)\n   return a if t else J(X(f,lambda h:E(F,'NEGE',[a,h])))",
    'leaf:and+': "if t:return E(f,'ANDI',[I(x,v),I(y,v)])",
    'leaf:and-': "z,i=(x,1)if not p else(y,2);a=I(z,v);return J(X(f,lambda h:E(F,'NEGE',[E(z,'ANDE%d'%i,[h]),a])))",
    'leaf:or+': "if t:return E(f,'ORI1',[I(x,v)])if p else E(f,'ORI2',[I(y,v)])",
    'leaf:or-': "a,c=I(x,v),I(y,v);return J(X(f,lambda h:E(F,'ORE',[h],[X(x,lambda u:E(F,'NEGE',[u,a])),X(y,lambda u:E(F,'NEGE',[u,c]))])))",
    'leaf:imp+B': "if q:c=I(y,v);return E(f,'IMPI',(),[X(x,lambda h:E(y,'R',[c]))])",
    'leaf:imp+A': "if not p:return E(f,'IMPI',(),[X(x,lambda h:E(y,'BOTE',[E(F,'NEGE',[h,a])]))])",
    'leaf:imp-': "c=I(y,v);return J(X(f,lambda h:E(F,'NEGE',[E(y,'IMPE',[h,a]),c])))",
}
DEMAND = ['explored', 'focus_h', 'target_h', 'decl_len', 'act_len', 'ref_dist', 'depth', 'state_len', 'log2_ops']


def group(tag):
    return 'close' if tag.startswith('close:') else tag


def snippet_sizes():
    src = open(A('kalmar_complexity/programs/python/ksl_alg.py')).read()
    lines = src.split('\n')
    out = {}
    try:
        from tokenizers import Tokenizer
        tq = Tokenizer.from_file(A('kalmar_complexity/tok/qwen3/tokenizer.json'))
    except Exception:
        tq = None
    for t, s in SNIP.items():
        assert s in src, t
        if s.startswith('def '):                           # a whole function: its header line and indented body
            i = next(j for j, l in enumerate(lines) if l.strip().startswith(s))
            ind = len(lines[i]) - len(lines[i].lstrip())
            j = i + 1
            while j < len(lines) and (len(lines[j]) - len(lines[j].lstrip()) > ind):
                j += 1
            s = '\n'.join(lines[i:j])
        out[t] = {'py_bytes': len(s.encode()), 'py_tokens': len(tq.encode(s).ids) if tq else None}
    return out


def spearman_perm(x, y, n_perm=100000, seed=0):
    x, y = np.asarray(x, float), np.asarray(y, float)
    rx, ry = stats.rankdata(x), stats.rankdata(y)
    r = np.corrcoef(rx, ry)[0, 1]
    rng = np.random.default_rng(seed)
    P = np.array([rng.permutation(ry) for _ in range(n_perm)])
    rp = ((P - P.mean(1, keepdims=True)) * (rx - rx.mean())).sum(1) / (
        np.sqrt(((P - P.mean(1, keepdims=True)) ** 2).sum(1)) * np.sqrt(((rx - rx.mean()) ** 2).sum()))
    return float(r), float((np.abs(rp) >= abs(r) - 1e-12).mean())


def logit_fit(X, y, iters=50, ridge=1e-6):
    w = np.zeros(X.shape[1])
    for _ in range(iters):
        z = X @ w
        p = 1 / (1 + np.exp(-z))
        g = X.T @ (y - p) - ridge * w
        H = (X * (p * (1 - p))[:, None]).T @ X + ridge * np.eye(X.shape[1])
        step = np.linalg.solve(H, g)
        w += step
        if np.abs(step).max() < 1e-8:
            break
    p = np.clip(1 / (1 + np.exp(-(X @ w))), 1e-12, 1 - 1e-12)
    return w, -2 * float((y * np.log(p) + (1 - y) * np.log(1 - p)).sum())


def main():
    PT = json.load(open(A('artifacts/kc/q4/per_type.json')))
    S = json.load(gzip.open(A('artifacts/kc/q4/states_tf1200.json.gz'), 'rt'))
    paths = json.load(open(A('artifacts/kc/q4/tree_paths_tf1200.json')))['paths']
    for s, d in zip(S, paths):
        s['tree_path'] = d
        s['log2_ops'] = math.log2(1 + s['ops'])
    types = [t for t, r in PT['types'].items() if r['states'] >= 500]
    tk = json.load(open(A('artifacts/kc/tokens_kal_sl.json')))['per_tag']
    freq = collections.Counter()
    for t, (n, _) in tk.items():
        freq[group(t)] += n
    snip = snippet_sizes()
    snap = json.load(open(A('artifacts/kc/b1_snap.json')))['models']
    pred = {t: {} for t in types}
    for t in types:
        idx = [i for i, s in enumerate(S) if group(s['tag']) == t]
        for k in DEMAND + ['tree_path']:
            pred[t][k] = float(np.mean([S[i][k] for i in idx]))
        pred[t]['log_freq'] = math.log10(freq[t])
        pred[t].update(snip.get(t, {}))
        fin = [m for m in snap if m.endswith(('stage1_kalD_s0.pt', 'stage1_kalD_s1.pt', 'stage1_kalD_s2.pt'))]
        tot = collections.Counter()
        for m in fin:
            for tg, v in snap[m]['per_tag'].items():
                if group(tg) == t:
                    tot['n'] += v['nats']; tot['k'] += v['loss_tokens']
        pred[t]['snap_final_nats_per_tok'] = tot['n'] / tot['k']
    extra = {}
    for f in ('artifacts/kc/q4/blc_per_type.json', 'artifacts/kc/q4/rasp_per_type.json', 'artifacts/kc/q4/b2_per_type.json'):
        if os.path.exists(A(f)):
            for t, d in json.load(open(A(f))).items():
                if t in pred:
                    pred[t].update(d)
                    extra.update({k: f for k in d})
    outcomes = {'kalD_mean': [np.mean([PT['types'][t][f'err_kalD_s{s}'] for s in range(3)]) for t in types]}
    for m in ['kalD_s0', 'kalD_s1', 'kalD_s2', 'kalDA_s0', 'kalDA_s1', 'kalDA_s2', 'kalC_s0']:
        outcomes[m] = [PT['types'][t]['err_' + m] for t in types]
    outcomes['kalDA_mean'] = [np.mean([PT['types'][t][f'err_kalDA_s{s}'] for s in range(3)]) for t in types]
    names = sorted({k for t in types for k in pred[t] if pred[t][k] is not None})
    res = {'types': types, 'predictors': {t: pred[t] for t in types},
           'outcomes': {k: dict(zip(types, map(float, v))) for k, v in outcomes.items()}, 'spearman': {}}
    print(f'{len(types)} step types with >= 500 states')
    print(f"{'predictor':24} " + ' '.join(f'{o:>14}' for o in ['kalD_mean', 'kalD_s0', 'kalD_s1', 'kalD_s2', 'kalDA_mean']))
    for k in names:
        ts = [t for t in types if pred[t].get(k) is not None]
        if len(ts) < 6:
            continue
        x = [pred[t][k] for t in ts]
        row = {}
        cells = []
        for o in ['kalD_mean', 'kalD_s0', 'kalD_s1', 'kalD_s2', 'kalDA_mean']:
            y = [outcomes[o][types.index(t)] for t in ts]
            r, p = spearman_perm(x, y)
            row[o] = {'rho': r, 'p': p, 'n': len(ts)}
            cells.append(f'{r:+.2f} (p {p:.3f})')
        res['spearman'][k] = row
        print(f'{k:24} ' + ' '.join(f'{c:>14}' for c in cells))
    # partial Spearman across types, controlling for log frequency (ranks residualised on the frequency rank)
    res['partial_spearman_given_log_freq'] = {}
    z = stats.rankdata([pred[t]['log_freq'] for t in types])
    ry = stats.rankdata(outcomes['kalD_mean'])

    def resid(a, b):
        M = np.vstack([b, np.ones_like(b)]).T
        return a - M @ np.linalg.lstsq(M, a, rcond=None)[0]
    print('\npartial Spearman | log_freq (KAL-D mean):')
    for k in names:
        if k == 'log_freq' or any(pred[t].get(k) is None for t in types):
            continue
        ex, ey = resid(stats.rankdata([pred[t][k] for t in types]), z), resid(ry, z)
        r = float(np.corrcoef(ex, ey)[0, 1])
        rng = np.random.default_rng(1)
        pp = float(np.mean([abs(np.corrcoef(ex, rng.permutation(ey))[0, 1]) >= abs(r) - 1e-12 for _ in range(20000)]))
        res['partial_spearman_given_log_freq'][k] = {'rho': r, 'p': pp}
        print(f'  {k:24} {r:+.2f} (p {pp:.3f})')
    # state level
    print('\nstate level: logistic regression of error on type dummies (+ standardised demand measures)')
    T = sorted({group(s['tag']) for s in S})
    D = np.array([[s[k] for k in DEMAND] for s in S], float)
    D = (D - D.mean(0)) / np.where(D.std(0) > 0, D.std(0), 1)
    Xt = np.array([[1.0] + [float(group(s['tag']) == t) for t in T[1:]] for s in S])
    agree = {}
    for m in ['kalD_s0', 'kalD_s1', 'kalD_s2']:
        d = json.loads(os.popen(f"git -C {ROOT} show HEAD:artifacts/kalmar/tf/{m}__tf1200.json").read())
        agree[m] = np.array([c == '0' for row in d['rows'] for c in row['agree']], float)
    res['state_level'] = {}
    for m, y in agree.items():
        w0, dev0 = logit_fit(Xt, y)
        w1, dev1 = logit_fit(np.hstack([Xt, D]), y)
        lr = dev0 - dev1
        p = float(stats.chi2.sf(lr, len(DEMAND)))
        single = {}
        for j, k in enumerate(DEMAND):
            _, dj = logit_fit(np.hstack([Xt, D[:, [j]]]), y)
            single[k] = {'lr': dev0 - dj, 'p': float(stats.chi2.sf(dev0 - dj, 1)), 'coef': None}
        coefs = dict(zip(DEMAND, map(float, w1[len(T):])))
        res['state_level'][m] = {'dev_type_only': dev0, 'dev_type_demand': dev1, 'lr': lr, 'df': len(DEMAND),
                                 'p': p, 'coef_std': coefs, 'single_lr': single}
        best = sorted(single.items(), key=lambda kv: -kv[1]['lr'])[:4]
        print(f"{m}: LR {lr:.0f} (df {len(DEMAND)}), p {p:.2g}; joint coefs " +
              ', '.join(f'{k} {v:+.2f}' for k, v in coefs.items()) + '; best single: ' +
              ', '.join(f"{k} LR {v['lr']:.0f}" for k, v in best))
    json.dump(res, open(A('artifacts/kc/q4/q4_results.json'), 'w'), indent=1)


if __name__ == '__main__':
    main()
