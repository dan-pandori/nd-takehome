#!/usr/bin/env python3
"""trajectory-cap6: cap 6 against cap 12, selection-free contrasts, per-stratum truncation.  Pure python + numpy/matplotlib
(runs on the VPS from pulled files).
  python3 tj6_compare.py            stdout = the tables; writes artifacts/tj6/compare.json, figures/tj6_joint.png,
                                    figures/tj6_b6a12.png
Models: cap 6 = best-cap6 s0-s2 (this run: ALiBiGPT 9,560,832 params, lean_staten, from scratch on the cap-6 set
p2 train_depth3_f0_a1, Stage-1 1,200 s + T1 ladder); cap 12 = best-cap12 s0-s2 (run `trajectory`, same recipe on K12).
Inputs: artifacts/tj6/eval, artifacts/tj6/score/{s<S>,cross_s<S>,rev12_s<K>}; cap12_in/{eval,score/s<K>} (trajectory's
files from hf://buckets/dan-pandori/nd-rl/trajectory/artifacts/tj/).
Definitions (preregistration/trajectory-cap6.md): groups per seed from sample seed 0 (A pend solves, B r8 not pend, C
neither); majority sets A6/B6/C6 and A12/B12/C12 = the group in >= 2 of 3 seeds. w1 = worst step log p (T 1.0, nats).
"""
import collections, json, math, os
import numpy as np

STEPS = [0, 50, 100, 200, 400, 800, 1600, 3000, 5000, 8000, 12000, 16000, 20000]
PRE = [f'p{s}' for s in STEPS] + ['pend']
CK = PRE + [f'r{r}' for r in range(1, 9)]
POOLS = ('tb72', 'h250')
T = 'T1.0'
SEEDS = (0, 1, 2)
D6, D12 = 'artifacts/tj6', 'cap12_in'


def rj(p):
    return [json.loads(l) for l in open(p) if l.strip()]


def reads(d, s, ck, x):
    out = {}
    for pool in POOLS:
        p = f'{d}/eval/s{s}_{ck}__{pool}_x{x}.jsonl'
        if not os.path.exists(p):
            return None
        for r in rj(p):
            out[r['name']] = r
    return out


def groups(d, s):
    a, b = reads(d, s, 'pend', 0), reads(d, s, 'r8', 0)
    if a is None or b is None:
        return None
    return {n: 'A' if a[n]['n_ok'] else 'B' if b[n]['n_ok'] else 'C' for n in a}, {n: a[n].get('pool') for n in a}


def load(d):
    """{ck: {tid: T-record}} per seed, for one score dir."""
    if not os.path.isdir(d):
        return None
    meta = {m['tid']: m for m in rj(f'{d}/targets.jsonl')}
    sc = {}
    for f in os.listdir(d):
        if f.endswith('.jsonl') and f != 'targets.jsonl':
            ck = f[:-6].split('_', 1)[1]
            sc[ck] = {o['tid']: o[T] for o in rj(f'{d}/{f}')}
    return meta, sc


def med(xs):
    xs = [x for x in xs if x is not None]
    return float(np.median(xs)) if xs else None


def iqm_ci(vals, B=2000, seed=0):
    rng = np.random.default_rng(seed)
    vals = [np.array([x for x in v if x is not None], float) for v in vals]
    vals = [v for v in vals if len(v)]
    if not vals:
        return None
    meds = [float(np.median(v)) for v in vals]
    bs = [float(np.mean([np.median(rng.choice(v, len(v))) for v in vals])) for _ in range(B)]
    return {'per_seed': [round(m, 2) for m in meds], 'iqm': round(float(np.mean(meds)), 2),
            'ci95': [round(float(np.percentile(bs, 2.5)), 2), round(float(np.percentile(bs, 97.5)), 2)], 'n': [len(v) for v in vals]}


def main():
    out = {}
    G6 = {s: groups(D6, s) for s in SEEDS}
    G12 = {s: groups(D12, s) for s in SEEDS}
    names = sorted(G6[0][0]) if G6[0] else []
    pool = dict(G6[0][1]) if G6[0] else {}
    for s in SEEDS:   # eval rows carry no pool field in every version: take it from the file
        for p in POOLS:
            for d, G in ((D6, G6), (D12, G12)):
                f = f'{d}/eval/s{s}_pend__{p}_x0.jsonl'
                if os.path.exists(f):
                    for r in rj(f):
                        pool[r['name']] = p
    maj = {}
    for tag, G in (('6', G6), ('12', G12)):
        for n in names:
            c = collections.Counter(G[s][0][n] for s in SEEDS if G[s])
            g, k = c.most_common(1)[0] if c else ('?', 0)
            maj[(tag, n)] = g if k >= 2 else 'mixed'
    xt = collections.Counter((maj[('6', n)], maj[('12', n)]) for n in names)
    print('## majority groups: rows cap 6, columns cap 12 (theorems; >= 2 of 3 seeds, else "mixed")')
    cols = ['A', 'B', 'C', 'mixed']
    print('cap6 \\ cap12 | ' + ' | '.join(cols) + ' | total')
    for r in cols:
        print(f'{r} | ' + ' | '.join(str(xt[(r, c)]) for c in cols) + f' | {sum(xt[(r, c)] for c in cols)}')
    out['crosstab'] = {f'{r}|{c}': xt[(r, c)] for r in cols for c in cols}
    B6A12 = sorted(n for n in names if maj[('6', n)] == 'B' and maj[('12', n)] == 'A')
    A6A12 = sorted(n for n in names if maj[('6', n)] == 'A' and maj[('12', n)] == 'A')
    out['B6A12'] = B6A12
    print(f'B6∩A12: {len(B6A12)} (tb72 {sum(pool[n] == "tb72" for n in B6A12)}, h250 {sum(pool[n] == "h250" for n in B6A12)}); '
          f'A6∩A12: {len(A6A12)}')

    S6 = {s: load(f'{D6}/score/s{s}') for s in SEEDS}
    X6 = {s: load(f'{D6}/score/cross_s{s}') for s in SEEDS}
    S12 = {s: load(f'{D12}/score/s{s}') for s in SEEDS}
    R12 = {s: load(f'{D6}/score/rev12_s{s}') for s in SEEDS}

    def rec(L, s, ck, tid):
        return None if not L.get(s) else L[s][1].get(ck, {}).get(tid)

    def w1(L, s, ck, tid):
        o = rec(L, s, ck, tid)
        return None if o is None else o['w1']

    def dd(L, s, tid, a, b):
        x, y = w1(L, s, b, tid), w1(L, s, a, tid)
        return None if x is None or y is None else x - y

    # ---- headline + selection-free contrasts (cap 6, B per seed)
    print('\n## B (per seed): Δ_RL = w1(r8) − w1(pend), Δ_PT = w1(pend) − w1(p1600); medians over B, IQM over seeds [95 %]')
    chk = {}
    for kind, L, tidf in (('own eventual', S6, lambda s, n: [f'ev:{n}']),
                          ('reference', S6, lambda s, n: [f'ref:{n}']),
                          ('cross-seed eventual', X6, lambda s, n: [f'ev6s{k}:{n}' for k in SEEDS if k != s]),
                          ('cap-12 eventual', X6, lambda s, n: [f'ev12s{k}:{n}' for k in SEEDS])):
        def per(fn):
            vals = []
            for s in SEEDS:
                if not G6[s] or not L.get(s):
                    vals.append([]); continue
                v = []
                for n, g in G6[s][0].items():
                    if g != 'B':
                        continue
                    xs = [fn(s, t) for t in tidf(s, n)]
                    xs = [x for x in xs if x is not None]
                    if xs:
                        v.append(float(np.mean(xs)))   # several fixed proofs of one theorem: their mean
                vals.append(v)
            return vals
        rl = per(lambda s, t: dd(L, s, t, 'pend', 'r8'))
        pt = per(lambda s, t: dd(L, s, t, 'p1600', 'pend'))
        diff = per(lambda s, t: None if dd(L, s, t, 'pend', 'r8') is None or dd(L, s, t, 'p1600', 'pend') is None
                   else dd(L, s, t, 'pend', 'r8') - dd(L, s, t, 'p1600', 'pend'))
        w0 = per(lambda s, t: w1(L, s, 'pend', t)); w8 = per(lambda s, t: w1(L, s, 'r8', t))
        r = {'w1_pend': iqm_ci(w0), 'w1_r8': iqm_ci(w8), 'dRL': iqm_ci(rl), 'dPT': iqm_ci(pt), 'paired_dRL_minus_dPT': iqm_ci(diff)}
        if r['dRL'] and r['dPT']:
            r['seeds_dRL_gt_dPT'] = sum(a > b for a, b in zip(r['dRL']['per_seed'], r['dPT']['per_seed']))
        chk[kind] = r
        print(f'{kind}: ' + '; '.join(f'{k} {v}' for k, v in r.items()))
    out['B_contrasts'] = chk

    # ---- cap 6 vs cap 12 on B6∩A12 (pre-registered 4a-4e)
    print('\n## cap 6 vs cap 12 on B6∩A12 (pooled over seed pairs; medians)')
    c = {}
    nst = lambda L, s, tid: (L[s][0].get(tid) or {}).get('n_steps') if L.get(s) else None
    for nm, S_ in (('B6A12', B6A12), ('A6A12', A6A12)):
        c[f'n_steps_ev6_{nm}'] = med([nst(S6, s, f'ev:{n}') for s in SEEDS for n in S_])
        c[f'n_steps_ev12_{nm}'] = med([nst(S12, s, f'ev:{n}') for s in SEEDS for n in S_])
    c['4a_diff'] = None if c['n_steps_ev6_B6A12'] is None else c['n_steps_ev6_B6A12'] - c['n_steps_ev6_A6A12']
    pairs = [(s, k, n) for s in SEEDS for k in SEEDS for n in B6A12]
    c['4b_ev12_under6_pend_w1'] = med([w1(X6, s, 'pend', f'ev12s{k}:{n}') for s, k, n in pairs])
    c['4b_ev12_under12_pend_w1'] = med([w1(S12, k, 'pend', f'ev:{n}') for k in SEEDS for n in B6A12])
    idx = [(rec(S6, s, 'pend', f'ev:{n}') or {}).get('w1_idx') for s in SEEDS for n in B6A12]
    idx = [i for i in idx if i is not None]
    c['4c_frac_w1_idx_ge7'] = (sum(i + 1 >= 7 for i in idx) / len(idx)) if idx else None
    c['4c_n'] = len(idx)
    c['4d_ev12_under6_r8_minus_pend'] = med([dd(X6, s, f'ev12s{k}:{n}', 'pend', 'r8') for s, k, n in pairs])
    c['4e_ev12_under12_pend_minus_p1600'] = med([dd(S12, k, f'ev:{n}', 'p1600', 'pend') for k in SEEDS for n in B6A12])
    c['ev6_under6_pend_w1'] = med([w1(S6, s, 'pend', f'ev:{n}') for s in SEEDS for n in B6A12])
    c['ev6_under6_r8_w1'] = med([w1(S6, s, 'r8', f'ev:{n}') for s in SEEDS for n in B6A12])
    c['ev6_under12_pend_w1'] = med([w1(R12, k, 'pend', f'ev6s{s}:{n}') for s, k, n in pairs])
    c['ref_under6_pend_w1'] = med([w1(S6, s, 'pend', f'ref:{n}') for s in SEEDS for n in B6A12])
    c['ref_under12_pend_w1'] = med([w1(S12, k, 'pend', f'ref:{n}') for k in SEEDS for n in B6A12])
    for k, v in c.items():
        print(f'{k}: {v if not isinstance(v, float) else round(v, 3)}')
    out['B6A12_checks'] = c
    # rescore consistency: ev12 under cap-12 ckpts (rev12) vs trajectory's own records
    dm = [abs(w1(R12, k, ck, f'ev12s{k}:{n}') - w1(S12, k, ck, f'ev:{n}')) for k in SEEDS for ck in CK for n in names
          if w1(R12, k, ck, f'ev12s{k}:{n}') is not None and w1(S12, k, ck, f'ev:{n}') is not None]
    out['rescore_max_abs_w1_diff'] = max(dm) if dm else None
    print(f'\nre-score check (cap-12 eventual under cap-12 ckpts, this run vs trajectory): {len(dm)} pairs, max |Δw1| '
          f'{out["rescore_max_abs_w1_diff"]}')

    # ---- figures
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    xs = list(range(len(CK)))
    xtl = [c_[1:] if c_.startswith('p') and c_ != 'pend' else ('end' if c_ == 'pend' else c_) for c_ in CK]

    def axfmt(ax):
        ax.set_xticks(xs); ax.set_xticklabels(xtl, rotation=60, fontsize=7)
        ax.axvline(len(PRE) - 0.5, color='k', lw=0.8, ls='--'); ax.grid(alpha=0.25)

    def band(ax, getter, label, color, ls):
        m, lo, hi = [], [], []
        for ck in CK:
            v = [x for x in getter(ck) if x is not None]
            if v:
                p = np.percentile(v, [25, 50, 75]); lo.append(p[0]); m.append(p[1]); hi.append(p[2])
            else:
                lo.append(np.nan); m.append(np.nan); hi.append(np.nan)
        ax.plot(xs, m, ls, color=color, label=label, lw=1.6)
        ax.fill_between(xs, lo, hi, color=color, alpha=0.12)

    tracked = [n for n in names if maj[('6', n)] in 'AB' and maj[('12', n)] in 'AB']
    out['tracked_both'] = len(tracked)
    fig, axs = plt.subplots(1, 3, figsize=(16, 4.4))
    GC = {'A': '#2a6fdb', 'B': '#e8590c'}
    for j, (fld, lab, yl) in enumerate((('total', 'total log p', (-40, 1)), ('mean', 'per-step mean log p', (-6, 0.2)),
                                        ('w1', 'worst step log p', (-20, 0.5)))):
        ax = axs[j]
        for tag, L, G, ls in (('cap 6', S6, G6, '-'), ('cap 12', S12, G12, '--')):
            for g in 'AB':
                band(ax, lambda ck, L=L, G=G, g=g, fld=fld: [(rec(L, s, ck, f'ev:{n}') or {}).get(fld) for s in SEEDS if G[s]
                                                         for n in tracked if G[s][0].get(n) == g],
                     f'{tag} {g}', GC[g], ls)
        ax.set_ylim(*yl); ax.set_title(lab + ' (nats)', fontsize=10); axfmt(ax)
    axs[0].legend(fontsize=8)
    fig.suptitle(f'Eventual proof by group, cap 6 (solid) vs cap 12 (dashed): {len(tracked)} theorems in A/B at both caps '
                 '(majority); groups per seed; median, IQR over theorem-seed pairs. x: pretraining step | RL round', fontsize=10)
    fig.tight_layout(); fig.savefig('figures/tj6_joint.png', dpi=110); plt.close(fig)

    fig, axs = plt.subplots(1, 2, figsize=(13, 4.6))
    for j, (fld, lab, yl) in enumerate((('w1', 'worst step log p', (-20, 0.5)), ('total', 'total log p', (-50, 1)))):
        ax = axs[j]
        g = lambda L, s, ck, tid: (rec(L, s, ck, tid) or {}).get(fld)
        band(ax, lambda ck: [g(S6, s, ck, f'ev:{n}') for s in SEEDS for n in B6A12], 'cap-6 eventual under cap 6', '#e8590c', '-')
        band(ax, lambda ck: [g(X6, s, ck, f'ev12s{k}:{n}') for s, k, n in pairs], 'cap-12 eventual under cap 6', '#2a6fdb', '-')
        band(ax, lambda ck: [g(S12, k, ck, f'ev:{n}') for k in SEEDS for n in B6A12], 'cap-12 eventual under cap 12', '#2a6fdb', '--')
        band(ax, lambda ck: [g(R12, k, ck, f'ev6s{s}:{n}') for s, k, n in pairs], 'cap-6 eventual under cap 12', '#e8590c', '--')
        band(ax, lambda ck: [g(S6, s, ck, f'ref:{n}') for s in SEEDS for n in B6A12], 'reference under cap 6', '#5f6b7a', '-')
        ax.set_ylim(*yl); ax.set_title(lab + ' (nats)', fontsize=10); axfmt(ax)
    axs[0].legend(fontsize=7)
    fig.suptitle(f'B6∩A12 ({len(B6A12)} theorems: B at cap 6, A at cap 12, majority of seeds); median, IQR over '
                 'theorem-seed(-pair)s. x: pretraining step | RL round', fontsize=10)
    fig.tight_layout(); fig.savefig('figures/tj6_b6a12.png', dpi=110); plt.close(fig)

    # ---- truncation per stratum (pool x group x checkpoint x sample seed), cap 6
    TR = {}
    for s in SEEDS:
        if not G6[s]:
            continue
        for ck in CK:
            for x in (0, 1):
                r = reads(D6, s, ck, x)
                if r is None:
                    continue
                acc = collections.defaultdict(lambda: [0, 0])
                for n, row in r.items():
                    t = sum(1 for z in row['reasons'] if ('trunc' in z or 'step cap' in z or 'max_steps' in z))
                    k = (pool[n], G6[s][0][n]); acc[k][0] += t; acc[k][1] += row['n_tried']
                for k, (t, nn) in acc.items():
                    TR[f's{s}|{ck}|x{x}|{k[0]}|{k[1]}'] = t / nn
    out['trunc_strata'] = TR
    if TR:
        v = np.array(list(TR.values()))
        rlk = [k for k in TR if k.split('|')[1].startswith('r')]
        ptk = [k for k in TR if k.split('|')[1].startswith('p')]
        print(f'\n## truncation per stratum (s|ck|x|pool|group): {len(TR)} strata; > 0.1 %: {int((v > 0.001).sum())}; '
              f'max pretraining {max((TR[k], k) for k in ptk) if ptk else None}; max RL {max((TR[k], k) for k in rlk) if rlk else None}; '
              f'RL strata > 0.1 %: {sum(TR[k] > 0.001 for k in rlk)} / {len(rlk)}')
    json.dump(out, open(f'{D6}/compare.json', 'w'), indent=1, default=str)


if __name__ == '__main__':
    main()
