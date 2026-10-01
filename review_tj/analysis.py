#!/usr/bin/env python3
"""Reviewer (trajectory): pre-registered log-p quantities from the executor's per-step score files (step_lp, T 1.0),
recomputed with my own summaries (w1 = min step, totals, medians), groups from rv/recount.json (my recount)."""
import json, os, statistics as st, random, collections
R = os.path.expanduser('~/review/trajectory'); S = f'{R}/artifacts/tj/score'
CK = ['p0','p50','p100','p200','p400','p800','p1600','p3000','p5000','p8000','p12000','p16000','p20000','pend'] + [f'r{i}' for i in range(1,9)]
G = json.load(open(f'{R}/rv/recount.json'))['groups']
med = st.median
def kind(a):
    t = a.split()
    if t[0] == 'exact': return 'exact'
    h = t[t.index(':=') + 1]
    if h == 'Or.elim': return 'box:orelim'
    if h == '(' and t[t.index(':=') + 2] == 'fun': return 'box:neg' if t[3] == '(' and t[4] == '¬' else 'box:imp'
    return 'atom'
out = {}
def boot_iqm(per_seed_lists, f, n=2000, rng=random.Random(0)):
    vals = []
    for _ in range(n):
        vals.append(st.mean(f([rng.choice(L) for _ in L]) for L in per_seed_lists))
    vals.sort(); return vals[int(.025 * n)], vals[int(.975 * n)]
D = {}
for s in (0, 1, 2):
    tg = {json.loads(l)['tid']: json.loads(l) for l in open(f'{S}/s{s}/targets.jsonl')}
    TT = {json.loads(l)['tid']: json.loads(l) for f in (f'{R}/artifacts/tj/targets/targets_s{s}.jsonl', f'{R}/data/tj/ref_new8.jsonl') for l in open(f)}
    sc = {ck: {json.loads(l)['tid']: json.loads(l)['T1.0']['step_lp'] for l in open(f'{S}/s{s}/s{s}_{ck}.jsonl')} for ck in CK}
    g = G[str(s)]
    def grp(tid):
        m = tg[tid]; pool = 'tb72' if m['name'].startswith('textbook_') else 'h250'
        return g[f'{pool}:{m["name"]}']
    D[s] = (tg, sc, grp)
    # all tids in every ckpt?
    assert all(set(sc[ck]) == set(tg) for ck in CK), s
    ev = collections.defaultdict(list); ref = collections.defaultdict(list)
    for tid, m in tg.items():
        (ev if m['kind'] == 'ev' else ref)[grp(tid)].append(tid)
    w1 = lambda tid, ck: min(sc[ck][tid]); tot = lambda tid, ck: sum(sc[ck][tid]); mean = lambda tid, ck: tot(tid, ck) / len(sc[ck][tid])
    B, A = ev['B'], ev['A']
    o = out[s] = {'n_ev': {k: len(v) for k, v in ev.items()}, 'n_ref': {k: len(v) for k, v in ref.items()}}
    o['B_w1'] = {ck: med([w1(t, ck) for t in B]) for ck in CK}
    o['A_w1'] = {ck: med([w1(t, ck) for t in A]) for ck in CK}
    o['B_dRL'] = med([w1(t, 'r8') - w1(t, 'pend') for t in B]); o['B_dPT'] = med([w1(t, 'pend') - w1(t, 'p1600') for t in B])
    o['A_dRL'] = med([w1(t, 'r8') - w1(t, 'pend') for t in A]); o['A_dPT'] = med([w1(t, 'pend') - w1(t, 'p1600') for t in A])
    o['tot'] = {f'{G_}_{ck}': med([tot(t, ck) for t in ev[G_]]) for G_ in 'AB' for ck in ('p1600', 'pend', 'r1', 'r4', 'r8')}
    o['mean_r0'] = {G_: med([mean(t, 'pend') for t in ev[G_]]) for G_ in 'AB'}
    # concentration at r0 (B ev): w1 vs median of rest-of-steps mean; kind of w1
    rest = [ (tot(t, 'pend') - w1(t, 'pend')) / (len(sc['pend'][t]) - 1) for t in B if len(sc['pend'][t]) > 1]
    o['B_r0_w1_minus_restmed'] = med([w1(t, 'pend') for t in B]) - med(rest)
    kc = collections.Counter(); boxy = 0
    for t in B:
        lp = sc['pend'][t]; i = lp.index(min(lp)); acts = tg[t]['actions_b0']; k = kind(acts[i])
        closing = k == 'exact' and i != len(acts) - 1
        kc[k + (':closing' if closing else '')] += 1; boxy += k.startswith('box') or closing
    o['B_r0_w1_kind'] = dict(kc); o['B_r0_w1_boxy_frac'] = boxy / len(B)
    o['B_w1_late_PT'] = med([w1(t, 'pend') - w1(t, 'p8000') for t in B]); o['A_w1_late_PT'] = med([w1(t, 'pend') - w1(t, 'p8000') for t in A])
    C = ref['C']
    o['C_ref_w1'] = {ck: med([w1(t, ck) for t in C]) for ck in CK}
    o['C_ref_dRL'] = med([w1(t, 'r8') - w1(t, 'pend') for t in C])
    Bref = ref['B']
    o['B_ref_dRL'] = med([w1(t, 'r8') - w1(t, 'pend') for t in Bref]) if Bref else None
    o['B_ref_n'] = len(Bref)
    # lengths / term sizes of eventual proofs vs refs
    o['len'] = {f'{k}_{G_}': med([tg[t]['n_steps'] for t in (ev if k == 'ev' else ref)[G_]]) for k in ('ev', 'ref') for G_ in 'ABC' if (ev if k == 'ev' else ref)[G_]}
    o['tsize'] = {f'{k}_{G_}': med([tg[t]['term_size'] for t in (ev if k == 'ev' else ref)[G_]]) for k in ('ev', 'ref') for G_ in 'ABC' if (ev if k == 'ev' else ref)[G_]}
    o['nd_lines'] = {f'{k}_{G_}': med([TT[t]['proof'].count(' ; ') for t in (ev if k == 'ev' else ref)[G_]]) for k in ('ev', 'ref') for G_ in 'ABC' if (ev if k == 'ev' else ref)[G_]}
    o['_B'] = B; o['_A'] = A; o['_C'] = C
for s in (0, 1, 2):
    o = out[s]
    print(f'--- seed {s}: ev {o["n_ev"]} ref {o["n_ref"]}')
    print('  B med w1 p0/p1600/p8000/pend/r1/r4/r8:', ' '.join(f'{o["B_w1"][c]:.2f}' for c in ('p0','p1600','p8000','pend','r1','r4','r8')))
    print('  A med w1 p0/p1600/p8000/pend/r1/r4/r8:', ' '.join(f'{o["A_w1"][c]:.2f}' for c in ('p0','p1600','p8000','pend','r1','r4','r8')))
    print(f'  B dRL {o["B_dRL"]:.2f} dPT {o["B_dPT"]:.2f} | A dRL {o["A_dRL"]:.2f} dPT {o["A_dPT"]:.2f}')
    print('  totals', {k: round(v, 2) for k, v in o['tot'].items()}, ' mean@r0', {k: round(v, 3) for k, v in o['mean_r0'].items()})
    print(f'  conc: B r0 med w1 - med rest = {o["B_r0_w1_minus_restmed"]:.2f}; w1 kinds {o["B_r0_w1_kind"]} boxy {o["B_r0_w1_boxy_frac"]:.2f}')
    print(f'  late PT (pend - p8000): B {o["B_w1_late_PT"]:.2f} A {o["A_w1_late_PT"]:.2f}')
    print('  C ref med w1:', ' '.join(f'{c}:{o["C_ref_w1"][c]:.2f}' for c in CK), f' dRL {o["C_ref_dRL"]:.2f}')
    print(f'  B ref n {o["B_ref_n"]} dRL {o["B_ref_dRL"]}  vs B ev dRL {o["B_dRL"]:.2f}')
    print('  steps', o['len'], ' term size', o['tsize'], ' ND lines', o['nd_lines'])
# across seeds: IQM (= mean at n=3) + stratified bootstrap (theorems within seed)
def w1d(s, t, a, b): return min(D[s][1][a][t]) - min(D[s][1][b][t])
for name, a, b in (('B dRL', 'r8', 'pend'), ('B dPT', 'pend', 'p1600')):
    per = [[w1d(s, t, a, b) for t in out[s]['_B']] for s in (0, 1, 2)]
    vals = [med(L) for L in per]; lo, hi = boot_iqm(per, med)
    print(f'{name}: per-seed {[round(v,2) for v in vals]} IQM {st.mean(vals):.2f} [{lo:.2f},{hi:.2f}] seed SD {st.stdev(vals):.2f}')
per = [[w1d(s, t, 'r8', 'pend') - w1d(s, t, 'pend', 'p1600') for t in out[s]['_B']] for s in (0, 1, 2)]
vals = [med(L) for L in per]; lo, hi = boot_iqm(per, med)
print(f'B paired (dRL - dPT): per-seed {[round(v,2) for v in vals]} IQM {st.mean(vals):.2f} [{lo:.2f},{hi:.2f}]')
per = [[min(D[s][1]['pend'][t]) for t in out[s]['_B']] for s in (0, 1, 2)]
vals = [med(L) for L in per]; lo, hi = boot_iqm(per, med)
print(f'B w1(r0): per-seed {[round(v,2) for v in vals]} IQM {st.mean(vals):.2f} [{lo:.2f},{hi:.2f}] SD {st.stdev(vals):.2f}')
json.dump({str(k): {kk: vv for kk, vv in v.items() if not kk.startswith('_')} for k, v in out.items()}, open(f'{R}/rv/analysis.json', 'w'), indent=1)
