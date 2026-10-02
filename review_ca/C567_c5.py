#!/usr/bin/env python3
"""C5 recount (reviewer, independent): trajectory (cap 12) and trajectory-cap6 worst-step numbers.
Inputs: rv/C567_raw/<run>/artifacts/<a>/{eval,score}/ fetched from hf://buckets/dan-pandori/nd-rl (C567_fetch.sh).
Groups from x0 reads at pend (r0) / r8; w1 from score files (T1.0 block). Own code; no run analysis scripts."""
import json, math, random, statistics as st, sys, os

R = '/home/dan/review/claim-audit/rv/C567_raw'
RUNS = {'cap12': 'trajectory/artifacts/tj', 'cap6': 'trajectory-cap6/artifacts/tj6'}
CK = ['p1600', 'p8000', 'pend', 'r1', 'r4', 'r8']


def solved(run, s, ck, x):
    out = {}
    for p in ('h250', 'tb72'):
        for l in open(f'{R}/{RUNS[run]}/eval/s{s}_{ck}__{p}_{x}.jsonl'):
            r = json.loads(l)
            out[r['name']] = (bool(r['solved']), r['n_ok'], r['n_tried'])
    return out


def groups(run, s, x):
    a, b = solved(run, s, 'pend', x), solved(run, s, 'r8', x)
    g = {}
    for n in a:
        g[n] = 'A' if a[n][0] else ('B' if b[n][0] else 'C')
    lost = sum(1 for n in a if a[n][0] and not b[n][0])
    return g, lost


def scores(run, s):
    sc = {}
    for ck in CK:
        for l in open(f'{R}/{RUNS[run]}/score/s{s}/s{s}_{ck}.jsonl'):
            r = json.loads(l)
            t = r['T1.0']
            sc.setdefault(r['tid'], {})[ck] = (t['w1'], t['total'], t.get('w2'), t['step_lp'])
    return sc


def med(v):
    return st.median(v) if v else float('nan')


def boot_iqm(per_seed_lists, f, B=2000, seed=0):
    """stratified bootstrap over theorems within seed; statistic = mean over seeds of per-seed median of f."""
    rng = random.Random(seed); out = []
    for _ in range(B):
        out.append(st.mean(med([f(rng.choice(L)) for _ in L]) for L in per_seed_lists))
    out.sort(); return out[int(.025 * B)], out[int(.975 * B) - 1]


res = {}
for run in RUNS:
    print(f'\n=== {run} ===')
    per = {}
    for s in (0, 1, 2):
        g0, lost = groups(run, s, 'x0')
        g1, _ = groups(run, s, 'x1')
        sc = scores(run, s)
        cnt = {k: sum(1 for v in g0.values() if v == k) for k in 'ABC'}
        B = [n for n, v in g0.items() if v == 'B']
        Bx1 = [n for n, v in g1.items() if v == 'B']
        Bboth = [n for n in B if g1[n] != 'A']   # r0 fails in both draws
        ev = lambda n, ck: sc.get('ev:' + n, {}).get(ck)
        rf = lambda n, ck: sc.get('ref:' + n, {}).get(ck)
        row = {'cnt': cnt, 'lost': lost}
        def stats(names, getter):
            L = [n for n in names if getter(n, 'pend') and getter(n, 'r8') and getter(n, 'p1600')]
            return L, {'n': len(L),
                       'w1_r0': med([getter(n, 'pend')[0] for n in L]),
                       'w1_r8': med([getter(n, 'r8')[0] for n in L]),
                       'dRL': med([getter(n, 'r8')[0] - getter(n, 'pend')[0] for n in L]),
                       'dPT': med([getter(n, 'pend')[0] - getter(n, 'p1600')[0] for n in L]),
                       'tot_r0': med([getter(n, 'pend')[1] for n in L]),
                       'w2_r0': med([getter(n, 'pend')[2] for n in L if getter(n, 'pend')[2] is not None]),
                       'rest_r0': med([getter(n, 'pend')[1] - getter(n, 'pend')[0] for n in L]),
                       'n_below4_r0': med([sum(1 for x in getter(n, 'pend')[3] if x < -4) for n in L])}
        LB, row['B_ev'] = stats(B, ev)
        _, row['B_ref'] = stats(B, rf)
        _, row['Bx1_ev'] = stats(Bx1, ev)
        _, row['Bboth_ev'] = stats(Bboth, ev)
        _, row['C_ref'] = stats([n for n, v in g0.items() if v == 'C'], rf)
        # selection check: x0-defined B, r0 success on independent x1 draw
        x1r0 = solved(run, s, 'pend', 'x1')
        row['B_x1_r0_solved'] = sum(1 for n in B if x1r0[n][0])
        row['B_x1_r0_rate'] = sum(x1r0[n][1] for n in B) / sum(x1r0[n][2] for n in B)
        per[s] = (row, LB, sc)
        print(f"s{s} groups A/B/C {cnt['A']}/{cnt['B']}/{cnt['C']} lost {lost} | B r0 solved on x1: {row['B_x1_r0_solved']}/{len(B)}, rate {row['B_x1_r0_rate']:.5f}")
        for k in ('B_ev', 'B_ref', 'Bx1_ev', 'Bboth_ev', 'C_ref'):
            d = row[k]
            print(f"   {k:9s} n={d['n']:3d} w1 r0 {d['w1_r0']:7.2f} r8 {d['w1_r8']:6.2f} dRL {d['dRL']:5.2f} dPT {d['dPT']:5.2f} "
                  f"tot_r0 {d['tot_r0']:6.1f} w2_r0 {d['w2_r0']:6.2f} rest_r0 {d['rest_r0']:6.1f} n<-4 {d['n_below4_r0']}")
    # pooled + IQM(=mean of 3 per-seed medians) with bootstrap
    for key, pre in (('B_ev', 'ev:'), ('B_ref', 'ref:')):
        lists = []
        pooled_r0 = []; pooled_dRL = []
        for s in (0, 1, 2):
            row, LB, sc = per[s]
            L = [sc[pre + n] for n in LB if pre + n in sc]
            lists.append(L)
            pooled_r0 += [x['pend'][0] for x in L]; pooled_dRL += [x['r8'][0] - x['pend'][0] for x in L]
        iqm_r0 = st.mean(med([x['pend'][0] for x in L]) for L in lists)
        iqm_dRL = st.mean(med([x['r8'][0] - x['pend'][0] for x in L]) for L in lists)
        iqm_dPT = st.mean(med([x['pend'][0] - x['p1600'][0] for x in L]) for L in lists)
        ci_r0 = boot_iqm(lists, lambda x: x['pend'][0])
        ci_rl = boot_iqm(lists, lambda x: x['r8'][0] - x['pend'][0])
        print(f"  {key}: pooled median w1 r0 {med(pooled_r0):.2f} (1-in-{math.exp(-med(pooled_r0)):.0f}); IQM w1 r0 {iqm_r0:.2f} "
              f"[{ci_r0[0]:.2f},{ci_r0[1]:.2f}] (1-in-{math.exp(-iqm_r0):.0f}); IQM dRL {iqm_dRL:.2f} [{ci_rl[0]:.2f},{ci_rl[1]:.2f}]; IQM dPT {iqm_dPT:.2f}")
        res.setdefault(run, {})[key] = dict(iqm_w1_r0=iqm_r0, ci_r0=ci_r0, iqm_dRL=iqm_dRL, ci_dRL=ci_rl, iqm_dPT=iqm_dPT,
                                             pooled_w1_r0=med(pooled_r0))
    res[run]['per_seed'] = {s: per[s][0] for s in per}
    r = res[run]
    print(f"  ratio own/ref dRL (IQM): {r['B_ev']['iqm_dRL'] / r['B_ref']['iqm_dRL']:.2f}")
json.dump(res, open('/home/dan/review/claim-audit/rv/C567_c5_out.json', 'w'), indent=1, default=str)
