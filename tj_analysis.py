#!/usr/bin/env python3
"""trajectory: groups, pass@k and teacher-forced log p across checkpoints; figures, tables, pre-registered checks.
VPS-runnable (numpy + matplotlib, no torch).

  python3 tj_analysis.py [--seeds 0 1 2] [--pre]      stdout = the tables; writes artifacts/tj/summary.json, figures/tj_*.png

Models: best-cap12 recipe (`best-state`), 3 fresh seeds: ALiBiGPT 6 x 384, 9,560,832 params, `lean_staten`, from scratch
on K12 (`data/kh/train_k12.jsonl`, cap 12), Stage-1 1,200 s on one A40 with 14 kept checkpoints (s<S>_p<step>, s<S>_pend),
then the T1 ladder (s<S>_r1..r8; r0 = pend).  Lean alone decides (state env gate).
Inputs: artifacts/tj/eval/<ckpt>__<pool>_x<sample seed>.jsonl (state_eval rows: n_ok of 256), artifacts/tj/score/s<S>/
(<ckpt>.jsonl, targets.jsonl from tj_score.py), artifacts/tj/score/pre_s<S>/ (--pre: refs under pretraining only).
Groups (seed-0 samples at pend and r8): A pend solves; B r8 solves, pend does not; C neither; A-lost = A and not r8.
"""
import argparse, collections, hashlib, json, math, os, statistics as stt
import numpy as np

STEPS = [0, 50, 100, 200, 400, 800, 1600, 3000, 5000, 8000, 12000, 16000, 20000]
PRE = [f'p{s}' for s in STEPS] + ['pend']
RL = [f'r{r}' for r in range(1, 9)]
CK = PRE + RL
POOLS = ('tb72', 'h250')
KS = (1, 8, 64, 256)
KEY = {'init': 'p0', 'mid-pretraining (12k)': 'p12000', 'end of pretraining (r0)': 'pend', 'RL r1': 'r1', 'RL r4': 'r4',
       'RL r8': 'r8'}
YLIM = {'total': (-40, 1), 'mean': (-6, 0.2), 'w1': (-20, 0.5)}   # init / earliest checkpoints lie far below (table)
GC = {'A': '#2a6fdb', 'B': '#e8590c', 'C': '#5f6b7a'}
E = 'artifacts/tj/eval'


def rj(p):
    return [json.loads(l) for l in open(p) if l.strip()]


def passk(n, c, k):
    if n - c < k:
        return 1.0
    return 1.0 - math.comb(n - c, k) / math.comb(n, k)


def reads(s, ck, x):
    """{name: (n_ok, n_tried, pool)} for one checkpoint / sample seed, or None if a pool file is missing."""
    out = {}
    for pool in POOLS:
        p = f'{E}/s{s}_{ck}__{pool}_x{x}.jsonl'
        if not os.path.exists(p):
            return None
        for r in rj(p):
            out[r['name']] = (r['n_ok'], r['n_tried'], pool)
    return out


def groups(s):
    a, b = reads(s, 'pend', 0), reads(s, 'r8', 0)
    if a is None or b is None:
        return None
    g = {}
    for n in a:
        fz, rl = a[n][0] > 0, b[n][0] > 0
        g[n] = 'A' if fz else 'B' if rl else 'C'
    lost = sorted(n for n in a if a[n][0] > 0 and b[n][0] == 0)
    return g, lost, {n: a[n][2] for n in a}


def refine(m):
    """step kinds with tj_score's 'name' split by the term's shape: app (n n: ->E / not-E), proj (n .1 / n .2: and-E),
    elim (n .elim), copy (n)."""
    out = []
    for a, k in zip(m.get('actions_b0', []), m.get('step_kind', [])):
        if k == 'name':
            t = a.split(); r = t[t.index(':=') + 2:]
            k = 'app' if r and r[0].startswith('n') else 'proj' if r[:1] in (['.1'], ['.2']) else 'elim' if r[:1] == ['.elim'] else 'copy'
        out.append('andI' if k == '⟨' else k)
    return out


def scores(s, sub):
    d = f'artifacts/tj/score/{sub}'
    if not os.path.isdir(d):
        return None, None
    meta = {m['tid']: dict(m, step_kind=refine(m)) for m in rj(f'{d}/targets.jsonl')}
    sc = {}
    for ck in CK:
        p = f'{d}/s{s}_{ck}.jsonl'
        if os.path.exists(p):
            sc[ck] = {o['tid']: o for o in rj(p)}
    return meta, sc


def q(xs):
    xs = [x for x in xs if x is not None]
    if not xs:
        return (None, None, None)
    a = np.array(xs, float)
    return tuple(float(v) for v in np.percentile(a, [25, 50, 75]))


def iqm_ci(vals, B=2000, seed=0):
    """vals: list over seeds of arrays over theorems; per-seed median, IQM over seeds (= mean at n = 3), and a stratified
    bootstrap 95 % interval (theorems resampled within seed)."""
    rng = np.random.default_rng(seed)
    meds = [float(np.median(v)) for v in vals if len(v)]
    if not meds:
        return None
    def iqm(m):
        m = sorted(m); n = len(m)
        if n < 4:
            return float(np.mean(m))
        lo, hi = int(math.floor(n * 0.25)), int(math.ceil(n * 0.75))
        return float(np.mean(m[lo:hi]))
    bs = []
    for _ in range(B):
        bs.append(iqm([float(np.median(rng.choice(v, len(v)))) for v in vals if len(v)]))
    return {'per_seed': [round(m, 3) for m in meds], 'iqm': round(iqm(meds), 3),
            'ci95': [round(float(np.percentile(bs, 2.5)), 3), round(float(np.percentile(bs, 97.5)), 3)]}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--seeds', type=int, nargs='*', default=[0, 1, 2])
    ap.add_argument('--pre', action='store_true', help='intermediate: pretraining half only (refs from score/pre_s<S>)')
    ap.add_argument('--T', default='T1.0')
    a = ap.parse_args()
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    os.makedirs('figures', exist_ok=True)
    out = {'T': a.T, 'seeds': {}}
    cks = PRE if a.pre else CK

    # ---------------- per seed: groups, pass@k (seed 1), log p
    G, PK, PK0, LP, TRUNC = {}, {}, {}, {}, {}
    for s in a.seeds:
        gg = groups(s)
        if a.pre:
            ag = reads(s, 'pend', 0)
            if ag is None:
                continue
            g = {n: ('A' if ag[n][0] > 0 else 'notA') for n in ag}; lost = []; pool = {n: ag[n][2] for n in ag}
        else:
            if gg is None:
                print(f'seed {s}: groups not available yet'); continue
            g, lost, pool = gg
        G[s] = (g, pool)
        cnt = collections.Counter(g.values())
        out['seeds'][s] = {'groups': dict(cnt), 'groups_by_pool': {p: dict(collections.Counter(g[n] for n in g if pool[n] == p)) for p in POOLS},
                           'A_lost': lost}
        # sanity counts (seed 0, best-state protocol)
        for ck in ('pend', 'r8'):
            r0 = reads(s, ck, 0)
            if r0:
                out['seeds'][s][f'solved_x0_{ck}'] = {p: sum(1 for n in r0 if r0[n][2] == p and r0[n][0] > 0) for p in POOLS}
        PK[s] = {}; PK0.setdefault(s, {})
        for ck in cks:
            r0_ = reads(s, ck, 0)
            if r0_ is not None:      # sample seed 0 (every checkpoint since Dan's 15:46 message): a second, independent estimate
                PK0[s][ck] = {n: {k: passk(r0_[n][1], r0_[n][0], k) for k in KS} for n in r0_}
                out['seeds'][s].setdefault('solved_x0', {})[ck] = {p: sum(1 for n in r0_ if r0_[n][2] == p and r0_[n][0] > 0) for p in POOLS}
            r1 = reads(s, ck, 1)
            if r1 is None:
                continue
            PK[s][ck] = {n: {k: passk(r1[n][1], r1[n][0], k) for k in KS} for n in r1}
            out['seeds'][s].setdefault('solved_x1', {})[ck] = {p: sum(1 for n in r1 if r1[n][2] == p and r1[n][0] > 0) for p in POOLS}
            tr = []
            for pool_ in POOLS:
                sm = json.load(open(f'{E}/s{s}_{ck}__{pool_}_x1.json'))['env']['env_end']
                tr.append((sm.get('truncated', 0) + sm.get('step_cap', 0), sum(sm.values())))
            TRUNC.setdefault(s, {})[ck] = sum(t for t, _ in tr) / sum(n for _, n in tr)
        meta, sc = scores(s, f'pre_s{s}' if a.pre else f's{s}')
        if meta:
            LP[s] = (meta, sc)

    # ---------------- tables
    names_g = ['A', 'notA'] if a.pre else ['A', 'B', 'C']
    print(f'# trajectory analysis ({"pretraining half, INTERMEDIATE" if a.pre else "full"}); log p at {a.T}, nats; '
          'model: best-cap12 recipe, 9,560,832 params, lean_staten, from scratch on K12; Lean alone')
    print('\n## groups (seed-0 samples at pend / r8)')
    for s in out['seeds']:
        print(f"seed {s}: {out['seeds'][s]['groups']}  by pool {out['seeds'][s]['groups_by_pool']}  A-lost {len(out['seeds'][s]['A_lost'])}"
              f"  solved x0 pend {out['seeds'][s].get('solved_x0_pend')} r8 {out['seeds'][s].get('solved_x0_r8')}")

    def sel(pools):
        return lambda n, s: G[s][1][n] in pools

    for pname, pools in (('tb72', ('tb72',)), ('h250', ('h250',)), ('combined', POOLS)):
        inpool = sel(pools)
        # pass@k by group
        print(f'\n## {pname}: mean pass@k (sample seed 1, unbiased, n 256) by group; per seed, then mean over seeds')
        rows = {}
        for grp in names_g:
            for ck in cks:
                for k in KS:
                    per = []
                    for s in PK:
                        if ck not in PK[s]:
                            continue
                        xs = [PK[s][ck][n][k] for n in PK[s][ck] if G[s][0].get(n) == grp and inpool(n, s)]
                        if xs:
                            per.append(float(np.mean(xs)))
                    rows[(grp, ck, k)] = per
        for grp in names_g:
            line = [f'{grp:5s}']
            for lab, ck in KEY.items():
                if ck not in cks:
                    continue
                v = rows.get((grp, ck, 1)), rows.get((grp, ck, 256))
                if v[0]:
                    line.append(f"{ck}: @1 {np.mean(v[0]):.3f} @256 {np.mean(v[1]):.3f}")
            print('  '.join(line))
        out.setdefault('passk', {})[pname] = {f'{g}|{c}|{k}': v for (g, c, k), v in rows.items()}
        # log p by group
        for kind in ('ref', 'ev'):
            if not LP or (a.pre and kind == 'ev'):
                continue
            print(f'\n## {pname}: {kind} proof log p ({a.T}) by group: median [IQR] over theorem-seed pairs')
            for grp in names_g:
                if kind == 'ev' and grp == 'C':
                    continue
                line = [f'{grp:5s}']
                for lab, ck in KEY.items():
                    if ck not in cks:
                        continue
                    tot, w1, mean = [], [], []
                    for s, (meta, sc) in LP.items():
                        if ck not in sc:
                            continue
                        for n, gr in G[s][0].items():
                            if gr != grp or not inpool(n, s):
                                continue
                            o = sc[ck].get(f'{kind}:{n}')
                            if o:
                                tot.append(o[a.T]['total']); w1.append(o[a.T]['w1']); mean.append(o[a.T]['mean'])
                    if tot:
                        line.append(f"{ck}: tot {q(tot)[1]:.1f} w1 {q(w1)[1]:.2f} [{q(w1)[0]:.1f},{q(w1)[2]:.1f}] mean {q(mean)[1]:.2f} (n {len(tot)})")
                print('  '.join(line))

    # ---------------- figures
    xs = list(range(len(cks)))
    xt = [c[1:] if c.startswith('p') and c != 'pend' else ('end' if c == 'pend' else c) for c in cks]

    def axfmt(ax):
        ax.set_xticks(xs); ax.set_xticklabels(xt, rotation=60, fontsize=7)
        if not a.pre:
            ax.axvline(len(PRE) - 0.5, color='k', lw=0.8, ls='--')
        ax.grid(alpha=0.25)

    for pname, pools in (('tb72', ('tb72',)), ('h250', ('h250',)), ('combined', POOLS)):
        inpool = sel(pools)
        for kind in (['ref'] if a.pre else ['ev', 'ref']):
            if not LP:
                break
            fig, axs = plt.subplots(1, 3, figsize=(15, 4.2))
            for j, (fld, lab) in enumerate((('total', 'total log p'), ('mean', 'per-step mean log p'), ('w1', 'worst step log p'))):
                ax = axs[j]
                for grp in names_g:
                    if kind == 'ev' and grp == 'C':
                        continue
                    med, lo, hi = [], [], []
                    for ck in cks:
                        v = []
                        for s, (meta, sc) in LP.items():
                            if ck not in sc:
                                continue
                            v += [sc[ck][f'{kind}:{n}'][a.T][fld] for n, gr in G[s][0].items()
                                  if gr == grp and inpool(n, s) and f'{kind}:{n}' in sc[ck]]
                        l_, m_, h_ = q(v)
                        med.append(m_); lo.append(l_); hi.append(h_)
                    if all(m is None for m in med):
                        continue
                    c = GC.get(grp, '#888')
                    ax.plot(xs, [np.nan if m is None else m for m in med], color=c, lw=2, label=f'{grp}')
                    ax.fill_between(xs, [np.nan if m is None else m for m in lo], [np.nan if m is None else m for m in hi], color=c, alpha=0.18)
                ax.set_ylim(*YLIM[fld]); ax.set_title(lab + f' (axis clipped at {YLIM[fld][0]})', fontsize=10); axfmt(ax)
                if j == 0:
                    ax.set_ylabel(f'nats ({a.T})'); ax.legend(fontsize=8)
            fig.suptitle(f'{"eventual" if kind == "ev" else "reference"} proof, {pname}: median and IQR over theorem-seed pairs '
                         f'(seeds {sorted(LP)}); x: pretraining step (log-spaced) | RL round'
                         + ('  [INTERMEDIATE, unreviewed]' if a.pre else ''), fontsize=10)
            fig.tight_layout(); fig.savefig(f'figures/tj_{"pre_" if a.pre else ""}{kind}_{pname}.png', dpi=110); plt.close(fig)
        # pass@k
        fig, axs = plt.subplots(1, 4, figsize=(17, 4))
        for j, k in enumerate(KS):
            ax = axs[j]
            for grp in names_g:
                c = GC.get(grp, '#888')
                for s in PK:
                    ys = [np.mean([PK[s][ck][n][k] for n in PK[s][ck] if G[s][0].get(n) == grp and inpool(n, s)] or [np.nan])
                          if ck in PK[s] else np.nan for ck in cks]
                    ax.plot(xs, ys, color=c, lw=1.4, alpha=0.8, label=grp if s == min(PK) else None)
                    if s in PK0:
                        y0 = [np.mean([PK0[s][ck][n][k] for n in PK0[s][ck] if G[s][0].get(n) == grp and inpool(n, s)] or [np.nan])
                              if ck in PK0[s] else np.nan for ck in cks]
                        ax.plot(xs, y0, color=c, lw=0.8, ls=':', alpha=0.8, label=f'{grp} (sample seed 0)' if s == min(PK) and j == 0 else None)
            ax.set_title(f'pass@{k}: solid sample seed 1, dotted seed 0 (defines groups)', fontsize=9); ax.set_ylim(-0.02, 1.02); axfmt(ax)
            if j == 0:
                ax.legend(fontsize=8)
        fig.suptitle(f'pass@k by group, {pname}; one line per training seed' + ('  [INTERMEDIATE, unreviewed]' if a.pre else ''), fontsize=10)
        fig.tight_layout(); fig.savefig(f'figures/tj_{"pre_" if a.pre else ""}passk_{pname}.png', dpi=110); plt.close(fig)

    # ---------------- heatmaps (seed 0; pre-registered rule: 4 smallest sha1(name) per group with 6-14 actions)
    if not a.pre and 0 in LP:
        meta, sc = LP[0]
        ex = {}
        for grp in ('A', 'B', 'C'):
            kind = 'ref' if grp == 'C' else 'ev'
            cand = [n for n, gr in G[0][0].items() if gr == grp and meta.get(f'{kind}:{n}', {}).get('replay_ok')
                    and 6 <= meta[f'{kind}:{n}']['n_steps'] <= 14]
            ex[grp] = [(n, kind) for n in sorted(cand, key=lambda n: hashlib.sha1(n.encode()).hexdigest())[:4]]
        fig, axs = plt.subplots(3, 4, figsize=(20, 13))
        for i, grp in enumerate(('A', 'B', 'C')):
            for j in range(4):
                ax = axs[i][j]
                if j >= len(ex[grp]):
                    ax.axis('off'); continue
                n, kind = ex[grp][j]
                tid = f'{kind}:{n}'
                M = np.array([sc[ck][tid][a.T]['step_lp'] for ck in CK if ck in sc])
                im = ax.imshow(M.T, aspect='auto', cmap='magma', vmin=-12, vmax=0)
                ax.set_xticks(range(len(M))); ax.set_xticklabels([xt[CK.index(c)] for c in CK if c in sc], rotation=90, fontsize=6)
                ax.axvline(len(PRE) - 0.5, color='w', lw=0.8, ls='--')
                ax.set_yticks(range(M.shape[1])); ax.set_yticklabels([f'{t}: {k}' for t, k in enumerate(meta[tid]['step_kind'])], fontsize=6)
                ax.set_title(f'{grp} {n[:22]} ({kind}, {meta[tid]["n_steps"]} steps)', fontsize=8)
        fig.colorbar(im, ax=axs, shrink=0.6, label=f'log p of the step ({a.T}, nats; clipped at -12)')
        fig.suptitle('per-step log p across checkpoints, seed 0; rows: steps (kind); columns: pretraining steps | RL rounds', fontsize=11)
        fig.savefig('figures/tj_heatmaps.png', dpi=100); plt.close(fig)
        out['heatmap_examples'] = ex

    # ---------------- pre-registered checks
    if not a.pre and LP:
        chk = {}
        def w1(s, kind, n, ck):
            o = LP[s][1].get(ck, {}).get(f'{kind}:{n}')
            return None if o is None else o[a.T]['w1']
        def grp_vals(fn, grp, pools=POOLS):
            vals = []
            for s in LP:
                v = [fn(s, n) for n, gr in G[s][0].items() if gr == grp and G[s][1][n] in pools]
                vals.append(np.array([x for x in v if x is not None]))
            return vals
        chk['B_ev_w1_r0'] = iqm_ci(grp_vals(lambda s, n: w1(s, 'ev', n, 'pend'), 'B'))
        chk['B_ev_w1_r8'] = iqm_ci(grp_vals(lambda s, n: w1(s, 'ev', n, 'r8'), 'B'))
        dRL = lambda kind: (lambda s, n: None if w1(s, kind, n, 'r8') is None else w1(s, kind, n, 'r8') - w1(s, kind, n, 'pend'))
        dPT = lambda kind: (lambda s, n: None if w1(s, kind, n, 'pend') is None else w1(s, kind, n, 'pend') - w1(s, kind, n, 'p1600'))
        dLate = lambda kind: (lambda s, n: None if w1(s, kind, n, 'pend') is None else w1(s, kind, n, 'pend') - w1(s, kind, n, 'p8000'))
        chk['B_ev_dRL'] = iqm_ci(grp_vals(dRL('ev'), 'B')); chk['B_ev_dPT'] = iqm_ci(grp_vals(dPT('ev'), 'B'))
        chk['B_ev_dRL_minus_dPT'] = iqm_ci(grp_vals(lambda s, n: None if dRL('ev')(s, n) is None else dRL('ev')(s, n) - dPT('ev')(s, n), 'B'))
        chk['B_ref_dRL'] = iqm_ci(grp_vals(dRL('ref'), 'B'))
        chk['B_ev_late_pt'] = iqm_ci(grp_vals(dLate('ev'), 'B')); chk['A_ev_late_pt'] = iqm_ci(grp_vals(dLate('ev'), 'A'))
        chk['C_ref_w1'] = {ck: iqm_ci(grp_vals(lambda s, n, ck=ck: w1(s, 'ref', n, ck), 'C')) for ck in CK}
        chk['C_ref_dRL'] = iqm_ci(grp_vals(dRL('ref'), 'C'))
        tot = lambda kind, ck: (lambda s, n: (LP[s][1].get(ck, {}).get(f'{kind}:{n}') or {}).get(a.T, {}).get('total'))
        for grp in ('A', 'B'):
            for ck in ('pend', 'r8'):
                chk[f'{grp}_ev_total_{ck}'] = iqm_ci(grp_vals(tot('ev', ck), grp))
        conc = lambda s, n: (lambda o: None if o is None else o[a.T]['w1'] - o[a.T]['rest_mean'])(LP[s][1]['pend'].get(f'ev:{n}'))
        chk['B_ev_w1_minus_restmean_r0'] = iqm_ci(grp_vals(conc, 'B'))
        kinds = collections.Counter()
        for s in LP:
            for n, gr in G[s][0].items():
                o = LP[s][1]['pend'].get(f'ev:{n}')
                if gr == 'B' and o:
                    kinds[LP[s][0][f'ev:{n}']['step_kind'][o[a.T]['w1_idx']]] += 1
        chk['B_ev_w1_kind_r0'] = dict(kinds.most_common())
        out['checks'] = chk
        print('\n## pre-registered quantities (per-seed medians over the group, IQM over seeds, stratified bootstrap 95 %)')
        for k, v in chk.items():
            if k != 'C_ref_w1':
                print(f'{k}: {v}')
        print('C_ref_w1 by ckpt (IQM):', {ck: (v or {}).get('iqm') for ck, v in chk['C_ref_w1'].items()})
    print('\n## truncation (action-truncated + step-capped, fraction of all seed-1 samples) per checkpoint')
    for s in TRUNC:
        print(f'seed {s}: ' + ' '.join(f'{ck} {v * 100:.2f}%' for ck, v in TRUNC[s].items()))
    out['truncation_x1'] = TRUNC
    json.dump(out, open(f'artifacts/tj/summary{"_pre" if a.pre else ""}.json', 'w'), indent=1, default=str)


if __name__ == '__main__':
    main()
