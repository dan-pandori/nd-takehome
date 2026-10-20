#!/usr/bin/env python3
"""Reviewer recount of Q4 (which measure predicts KAL-D's per-step-type teacher-forced error).

  python3 rv_q4.py          # needs out/states_tf1200.json.gz, out/b1_tokens_kal.json, out/b2_counts.json

Outcome: kalmar-pretrain's per-state agree strings (git show HEAD:artifacts/kalmar/tf/<m>__tf1200.json; '1' = the
greedy action equals the algorithm's), error = 1 - agree, joined to my state table by record name and position.
Types: builder tags, close:* grouped, >= 500 states.
Predictors I compute: explored, focus_h, target_h, decl_len, act_len, depth (rv_states.py), log_freq (my pair counts
per tag over K12-Kalmár), py_bytes (bytes of the executor's per-type snippets of ksl_alg.py; mapping theirs, count
mine), b2 bits per occurrence (B2 per_tag_bits summed over the prequential blocks / my occurrence counts),
tree_path (tests on the path of tree_u_b3.json for each tf1200 state, features from the executor's extractor).
Taken from the executor (labelled): rasp_* (rasp_per_type.json), log2_ops (their states file).
Spearman (scipy ranks) with a permutation p (20,000), partial Spearman given log_freq, and a state-level logistic
regression (own IRLS) of error on type dummies +/- my standardised demand measures, LR test per seed.
"""
import gzip, json, math, os, subprocess, sys, collections
import numpy as np
from scipy import stats
HERE = os.path.dirname(os.path.abspath(__file__))
WS = os.path.expanduser('~/review/kalmar-complexity')
WT = os.path.expanduser('~/work/kalmar-complexity')
sys.path.insert(0, WS); sys.path.insert(0, os.path.join(WS, 'kalmar'))


def grp(t):
    return 'close' if t.startswith('close:') else t


def perm(x, y, n=20000, seed=0):
    rx, ry = stats.rankdata(x), stats.rankdata(y)
    r = float(np.corrcoef(rx, ry)[0, 1])
    rng = np.random.default_rng(seed)
    ry0 = ry - ry.mean(); rx0 = rx - rx.mean()
    den = np.sqrt((rx0 ** 2).sum() * (ry0 ** 2).sum())
    P = np.array([rng.permutation(ry0) for _ in range(n)])
    rp = (P @ rx0) / den
    return r, float((np.abs(rp) >= abs(r) - 1e-12).mean())


def logit(X, y, iters=100):
    w = np.zeros(X.shape[1])
    for _ in range(iters):
        p = 1 / (1 + np.exp(-(X @ w)))
        g = X.T @ (y - p) - 1e-6 * w
        H = (X * (p * (1 - p))[:, None]).T @ X + 1e-6 * np.eye(X.shape[1])
        s = np.linalg.solve(H, g)
        w += s
        if np.abs(s).max() < 1e-9:
            break
    p = np.clip(1 / (1 + np.exp(-(X @ w))), 1e-12, 1 - 1e-12)
    return w, -2 * float((y * np.log(p) + (1 - y) * np.log(1 - p)).sum())


def main():
    S = json.load(gzip.open(os.path.join(HERE, 'out', 'states_tf1200.json.gz'), 'rt'))
    n = len(S)
    names = [json.loads(l)['name'] for l in open(os.path.join(WS, 'data/kalmar/tf1200_kal_sl.jsonl'))]
    rec_of = np.array([s['rec'] for s in S])
    G = np.array([grp(s['tag']) for s in S])
    types = sorted(t for t in set(G) if (G == t).sum() >= 500)
    # ---- outcomes
    err = {}
    for m in ['kalD_s0', 'kalD_s1', 'kalD_s2', 'kalDA_s0', 'kalDA_s1', 'kalDA_s2', 'kalC_s0', 'kalC_s1', 'kalC_s2']:
        d = json.loads(subprocess.run(['git', '-C', WT, 'show', f'HEAD:artifacts/kalmar/tf/{m}__tf1200.json'],
                                      capture_output=True, text=True).stdout)
        assert [r['name'] for r in d['rows']] == names, m
        s = ''.join(r['agree'] for r in d['rows'])
        assert len(s) == n, (m, len(s), n)
        # per-record lengths must match
        lens = collections.Counter(rec_of.tolist())
        assert all(len(r['agree']) == lens[i] for i, r in enumerate(d['rows'])), m
        err[m] = np.array([c != '1' for c in s], float)
    out = {'n_states': n, 'types': types, 'type_states': {t: int((G == t).sum()) for t in types}}
    perr = {m: {t: float(e[G == t].mean()) for t in types} for m, e in err.items()}
    perr['kalD_mean'] = {t: float(np.mean([perr[f'kalD_s{s}'][t] for s in range(3)])) for t in types}
    perr['kalDA_mean'] = {t: float(np.mean([perr[f'kalDA_s{s}'][t] for s in range(3)])) for t in types}
    out['per_type_error'] = perr
    out['overall_error'] = {m: float(e.mean()) for m, e in err.items()}
    # ---- predictors (mine)
    pred = {t: {} for t in types}
    for k in ['explored', 'focus_h', 'target_h', 'decl_len', 'act_len', 'depth']:
        arr = np.array([s[k] for s in S], float)
        for t in types:
            pred[t][k] = float(arr[G == t].mean())
    tk = json.load(open(os.path.join(HERE, 'out', 'b1_tokens_kal.json')))['per_tag']
    fr = collections.Counter()
    for tg, (p, _) in tk.items():
        fr[grp(tg)] += p
    for t in types:
        pred[t]['log_freq'] = math.log10(fr[t])
    # py snippets: the executor's mapping (q4_analysis.SNIP), my byte count
    sys.path.insert(0, os.path.join(WS, 'kalmar_complexity'))
    src = open(os.path.join(WS, 'kalmar_complexity/programs/python/ksl_alg.py')).read()
    import importlib.util
    spec = importlib.util.spec_from_file_location('q4a', os.path.join(WS, 'kalmar_complexity/q4_analysis.py'))
    txt = open(os.path.join(WS, 'kalmar_complexity/q4_analysis.py')).read()
    snip_src = txt[txt.index('SNIP = {'):txt.index('}\nDEMAND')] + '}'
    SNIP = eval(snip_src[len('SNIP = '):])
    lines = src.split('\n')
    for t in types:
        s = SNIP.get(t)
        if s is None:
            continue
        assert s in src
        if s.startswith('def '):
            i = next(j for j, l in enumerate(lines) if l.strip().startswith(s))
            ind = len(lines[i]) - len(lines[i].lstrip())
            j = i + 1
            while j < len(lines) and len(lines[j]) - len(lines[j].lstrip()) > ind:
                j += 1
            s = '\n'.join(lines[i:j])
        pred[t]['py_bytes'] = len(s.encode())
    # B2 bits per occurrence (prequential blocks only), per size (seed 0), Kalmár task
    C = json.load(open(os.path.join(HERE, 'out', 'b2_counts.json')))['kal']
    for size in ('S', 'M', 'L'):
        d = json.load(open(os.path.join(WS, f'artifacts/kc/b2/kal_{size}_s0.json')))
        T = d['args']['max_thm']
        bits = collections.Counter(); occ = collections.Counter()
        for b in d['blocks']:
            if b.get('asymptote_block'):
                continue
            for tg, v in b['per_tag_bits'].items():
                bits[grp(tg)] += v
        for r in C[:T]:
            for tg, c in r['tag_pairs'].items():
                occ[grp(tg)] += c
        for t in types:
            pred[t][f'b2_bits_per_occ_{size}'] = bits[t] / occ[t]
    # executor-provided predictors
    rp = json.load(open(os.path.join(WS, 'artifacts/kc/q4/rasp_per_type.json')))
    for t in types:
        if t in rp:
            for k, v in rp[t].items():
                pred[t]['exec_' + k] = v
    theirs = json.load(gzip.open(os.path.join(WS, 'artifacts/kc/q4/states_tf1200.json.gz'), 'rt'))
    assert len(theirs) == n
    agree_measures = {}
    for k in ['explored', 'focus_h', 'target_h', 'decl_len', 'act_len', 'depth']:
        agree_measures[k] = int(sum(1 for a, b in zip(S, theirs) if a[k] == b[k]))
    out['state_measures_agree_with_executor'] = agree_measures
    lops = np.array([math.log2(1 + x['ops']) for x in theirs])
    for t in types:
        pred[t]['exec_log2_ops'] = float(lops[G == t].mean())
    # tree path lengths with tree_u_b3 (executor's features)
    try:
        tp = json.load(open(os.path.join(HERE, 'out', 'tree_paths_tf1200.json')))
        arr = np.array(tp, float)
        for t in types:
            pred[t]['tree_path'] = float(arr[G == t].mean())
    except FileNotFoundError:
        pass
    out['predictors'] = pred
    # ---- Spearman
    keys = sorted({k for t in types for k in pred[t]})
    sp = {}
    for k in keys:
        ts = [t for t in types if k in pred[t]]
        x = [pred[t][k] for t in ts]
        row = {}
        for o in ['kalD_mean', 'kalD_s0', 'kalD_s1', 'kalD_s2', 'kalDA_mean']:
            row[o] = perm(x, [perr[o][t] for t in ts])
        row['n'] = len(ts)
        sp[k] = row
    out['spearman'] = sp
    # partial given log_freq
    z = stats.rankdata([pred[t]['log_freq'] for t in types])
    ry = stats.rankdata([perr['kalD_mean'][t] for t in types])

    def resid(a, b):
        M = np.vstack([b, np.ones_like(b)]).T
        return a - M @ np.linalg.lstsq(M, a, rcond=None)[0]
    part = {}
    rng = np.random.default_rng(1)
    for k in keys:
        if k == 'log_freq' or any(k not in pred[t] for t in types):
            continue
        ex_ = resid(stats.rankdata([pred[t][k] for t in types]), z)
        ey = resid(ry, z)
        r = float(np.corrcoef(ex_, ey)[0, 1])
        pp = float(np.mean([abs(np.corrcoef(ex_, rng.permutation(ey))[0, 1]) >= abs(r) - 1e-12 for _ in range(5000)]))
        part[k] = (r, pp)
    out['partial_given_log_freq'] = part
    # ---- state level
    DEM = ['explored', 'focus_h', 'target_h', 'decl_len', 'act_len', 'depth']
    D = np.array([[s[k] for k in DEM] for s in S], float)
    D = (D - D.mean(0)) / np.where(D.std(0) > 0, D.std(0), 1)
    allT = sorted(set(G))
    Xt = np.array([[1.0] + [float(g == t) for t in allT[1:]] for g in G])
    st = {}
    for m in ['kalD_s0', 'kalD_s1', 'kalD_s2']:
        y = err[m]
        w0, d0 = logit(Xt, y)
        w1, d1 = logit(np.hstack([Xt, D]), y)
        single = {}
        for j, k in enumerate(DEM):
            _, dj = logit(np.hstack([Xt, D[:, [j]]]), y)
            single[k] = d0 - dj
        st[m] = {'dev_type': d0, 'dev_type_demand': d1, 'LR': d0 - d1, 'df': len(DEM),
                 'p': float(stats.chi2.sf(d0 - d1, len(DEM))), 'coef': dict(zip(DEM, map(float, w1[len(allT):]))),
                 'single_LR': single}
    out['state_level'] = st
    json.dump(out, open(os.path.join(HERE, 'out', 'q4_recount.json'), 'w'), indent=1)
    print('types', types)
    print('per-type KAL-D mean error:', {t: round(perr['kalD_mean'][t], 4) for t in types})
    print('measures agree with executor (of %d):' % n, agree_measures)
    for k in keys:
        r = sp[k]
        print(f"{k:28} n={r['n']:2} mean {r['kalD_mean'][0]:+.2f} (p {r['kalD_mean'][1]:.3f})  s0 {r['kalD_s0'][0]:+.2f} "
              f"s1 {r['kalD_s1'][0]:+.2f} s2 {r['kalD_s2'][0]:+.2f}  DA {r['kalDA_mean'][0]:+.2f}"
              + (f"  partial|freq {part[k][0]:+.2f} (p {part[k][1]:.3f})" if k in part else ''))
    for m, v in st.items():
        print(m, 'LR', round(v['LR']), 'p', v['p'], {k: round(x) for k, x in v['single_LR'].items()})


if __name__ == '__main__':
    main()
