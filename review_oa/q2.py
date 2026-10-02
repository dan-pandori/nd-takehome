"""Reviewer Q2 recount: hard steps (ref step lp < -4 at r0), own classifier, per-class gains, matched controls."""
import json, collections, statistics as st
import numpy as np
from scipy.stats import spearmanr
import rvc
ROUNDS = {'c12': ['pend'] + [f'r{k}' for k in range(1, 9)], 'c6': ['pend'] + [f'r{k}' for k in range(1, 9)]}
steps = []
for run in ('c12', 'c6', 'rfc'):
    for seed in range(3):
        for st_ in (rvc.STARTS if run == 'rfc' else [None]):
            if run == 'rfc':
                cks = ['r0', 'r2', 'r4', 'r8']; S = {c: rvc.score('rfc', seed, c, st_) for c in cks}
                meta = rvc.tmeta('rfc', seed, st_)
                labs = [f's{seed}_{st_}_r{k}' for k in (2, 4, 8)]; rr = 'rfc'
                s0 = rvc.solved('c12', f's{seed}_{st_}', 0)
            else:
                cks = ROUNDS[run]; S = {c: rvc.score(run, seed, c) for c in cks}; meta = rvc.tmeta(run, seed)
                labs = [f's{seed}_r{k}' for k in range(1, 9)]; rr = run
                s0 = rvc.solved(run, f's{seed}_pend', 0)
            ever = set()
            for l in labs:
                for x in (0, 1): ever |= rvc.solved(rr, l, x)
            s8 = rvc.solved(rr, labs[-1], 0)
            for t, m in meta.items():
                if m['kind'] != 'ref': continue
                name = m['name']; lp0 = S[cks[0]][t]['step_lp']
                for i, a in enumerate(m['actions_b0']):
                    if lp0[i] < -4:
                        steps.append(dict(run=run, seed=seed, start=st_, name=name, i=i, cls=rvc.cls(a),
                                          lp={c: S[c][t]['step_lp'][i] for c in cks}, never=name not in ever,
                                          B=(name not in s0 and name in s8), A=name in s0))
json.dump(steps, open('rv/q2_steps.json', 'w'))
res = {}
for run in ('c12', 'c6', 'rfc'):
    H = [s for s in steps if s['run'] == run]; cks = list(H[0]['lp'])
    c = collections.Counter(s['cls'] for s in H); n = len(H)
    share_box_proj = sum(v for k, v in c.items() if k.startswith('box') or k == 'and_proj') / n
    per = {}
    for k, v in c.most_common():
        hs = [s for s in H if s['cls'] == k]
        d = lambda grp: [s['lp'][cks[-1]] - s['lp'][cks[0]] for s in grp]
        sol = [s for s in hs if not s['never']]; nev = [s for s in hs if s['never']]; B = [s for s in hs if s['B']]
        per[k] = dict(n=v, n_never=len(nev), med_by_round=[round(st.median(s['lp'][c_] for s in hs), 2) for c_ in cks],
                      dmed_solved=round(st.median(d(sol)), 2) if sol else None, dmean_solved=round(np.mean(d(sol)), 2) if sol else None,
                      dmed_B=round(st.median(d(B)), 2) if B else None,
                      dmed_never=round(st.median(d(nev)), 2) if nev else None,
                      seed_med_solved=[round(st.median(d([s for s in sol if s['seed'] == q])), 2) if [s for s in sol if s['seed'] == q] else None for q in range(3)])
    nev = [s for s in H if s['never']]
    dn = [s['lp'][cks[-1]] - s['lp'][cks[0]] for s in nev]
    # matched control: for each class, same-class never-solved steps vs other-class never-solved steps in same (seed,start,1-nat bin)
    def key(s): return (s['seed'], s['start'], int(np.floor(s['lp'][cks[0]])))
    pool = collections.defaultdict(list)
    for s in nev: pool[key(s)].append(s)
    mc = {}
    for k in c:
        diffs = []
        for s in nev:
            if s['cls'] != k: continue
            ctl = [o['lp'][cks[-1]] - o['lp'][cks[0]] for o in pool[key(s)] if o['cls'] != k]
            if ctl: diffs.append((s['lp'][cks[-1]] - s['lp'][cks[0]]) - np.mean(ctl))
        if diffs: mc[k] = dict(n=len(diffs), mean_minus_ctl=round(float(np.mean(diffs)), 2), med=round(float(np.median(diffs)), 2))
    ks = [k for k in c if per[k]['dmed_never'] is not None and per[k]['dmed_solved'] is not None and per[k]['n_never'] >= 5]
    rho = spearmanr([per[k]['dmed_never'] for k in ks], [per[k]['dmed_solved'] for k in ks])
    # partial R^2 of class in delta ~ lp0 + class (never-solved, and all)
    def pr2(G):
        y = np.array([s['lp'][cks[-1]] - s['lp'][cks[0]] for s in G]); x0 = np.array([s['lp'][cks[0]] for s in G])
        K = sorted({s['cls'] for s in G}); A = np.c_[np.ones(len(G)), x0]; Bm = np.c_[A, [[s['cls'] == k for k in K[1:]] for s in G]]
        r = lambda M: ((y - M @ np.linalg.lstsq(M, y, rcond=None)[0]) ** 2).sum()
        return round(float((r(A) - r(Bm)) / r(A)), 3)
    res[run] = dict(n_hard=n, classes=dict(c.most_common()), share_box_and_proj=round(share_box_proj, 3),
                    n_never=len(nev), med_delta_never=round(st.median(dn), 2), per=per, matched=mc,
                    classes_ge_half_0p5=f"{sum(v['mean_minus_ctl'] >= 0.5 for v in mc.values())}/{len(mc)}",
                    spearman=[round(float(rho[0]), 3), round(float(rho[1]), 3), len(ks)], pr2_never=pr2(nev), pr2_all=pr2(H),
                    seed_med_delta_never=[round(st.median([s['lp'][cks[-1]] - s['lp'][cks[0]] for s in nev if s['seed'] == q]), 2) for q in range(3)])
    print(run, json.dumps({k: v for k, v in res[run].items() if k != 'per'}))
    for k, v in per.items(): print('  ', k, v)
json.dump(res, open('rv/q2.json', 'w'), indent=1)
