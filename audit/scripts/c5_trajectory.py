"""C5 audit: trajectory (best-cap12) and trajectory-cap6 (best-cap6) worst-step findings, re-derived from raw reads + stored
per-step teacher-forced scores (T 1.0). Groups from x0 reads at pend (r0) and r8 using n_ok>0 (own code).
Sources (pulled run files): ~/work/trajectory/artifacts/tj/{eval,score}, ~/work/trajectory-cap6/artifacts/tj6/{eval,score},
~/work/rl-from-ckpt/artifacts/rfc/score/cpend_s*/ (replay-only control of the cap-12 end checkpoint)."""
import json, os, math, random, statistics as st, sys
HOME = os.path.expanduser('~')
RUNS = {'cap12': HOME + '/work/trajectory/artifacts/tj', 'cap6': HOME + '/work/trajectory-cap6/artifacts/tj6'}
OUT = '/home/dan/work/claim-audit/audit/out/'
med = st.median

def solved(path):
    d = {}
    for l in open(path):
        r = json.loads(l); d[r['name']] = r['n_ok'] > 0
    return d

def read(run, s, ck, x):
    d = {}
    for pool in ('tb72', 'h250'): d.update(solved(f'{RUNS[run]}/eval/s{s}_{ck}__{pool}_x{x}.jsonl'))
    return d

_sc = {}
def score(path):
    if path not in _sc:
        d = {}
        for l in open(path):
            r = json.loads(l); t = r['T1.0']; sl = sorted(t['step_lp'])
            d[r['tid']] = dict(w1=t['w1'], w2=t.get('w2', sl[1] if len(sl) > 1 else 0.0), tot=t['total'], n=len(sl), steps=t['step_lp'])
        _sc[path] = d
    return _sc[path]

def groups(run, s, x=0):
    r0, r8 = read(run, s, 'pend', x), read(run, s, 'r8', x)
    A = {n for n in r0 if r0[n]}; B = {n for n in r0 if not r0[n] and r8[n]}; C = {n for n in r0 if not r0[n] and not r8[n]}
    return A, B, C

def boot_med_diff(vals_a, vals_b, nb=2000, seed=0):
    rng = random.Random(seed); out = []
    for _ in range(nb):
        out.append(med([rng.choice(vals_a) for _ in vals_a]) - med([rng.choice(vals_b) for _ in vals_b]))
    out.sort(); return out[int(.025 * nb)], out[int(.975 * nb)]

res = {}
L400 = math.log(1 / 400)
for run in ('cap12', 'cap6'):
    print(f'\n===== {run} =====')
    for s in (0, 1, 2):
        A, B, C = groups(run, s)
        Bx1 = groups(run, s, 1)[1]
        r0x1 = read(run, s, 'pend', 1)
        sc = {ck: score(f'{RUNS[run]}/score/s{s}/s{s}_{ck}.jsonl') for ck in ('p1600', 'p8000', 'pend', 'r8')}
        row = dict(A=len(A), B=len(B), C=len(C), B_x0_solved_by_r0_x1=sum(r0x1[n] for n in B))
        for kind, G, gname in (('ev', B, 'B'), ('ref', B, 'B'), ('ref', C, 'C'), ('ev', A, 'A'), ('ref', A, 'A')):
            ids = [f'{kind}:{n}' for n in sorted(G) if f'{kind}:{n}' in sc['pend'] and f'{kind}:{n}' in sc['r8'] and f'{kind}:{n}' in sc['p1600']]
            w = {ck: [sc[ck][i]['w1'] for i in ids] for ck in sc}
            dRL = [b - a for a, b in zip(w['pend'], w['r8'])]; dPT = [b - a for a, b in zip(w['p1600'], w['pend'])]
            k = f'{gname}_{kind}'
            row[k] = dict(n=len(ids), w1_1600=med(w['p1600']), w1_r0=med(w['pend']), w1_r8=med(w['r8']),
                          dRL=med(w['r8']) - med(w['pend']), dPT=med(w['pend']) - med(w['p1600']),
                          dd=(med(w['r8']) - med(w['pend'])) - (med(w['pend']) - med(w['p1600'])),
                          paired_dd=med([a - b for a, b in zip(dRL, dPT)]), pdRL=med(dRL), pdPT=med(dPT),
                          frac_w1_lt_ln400_r0=sum(x < L400 for x in w['pend']) / len(ids),
                          frac_w2_lt_m4_r0=sum(sc['pend'][i]['w2'] < -4 for i in ids) / len(ids),
                          frac_w2_lt_ln400_r0=sum(sc['pend'][i]['w2'] < L400 for i in ids) / len(ids),
                          med_w2_r0=med([sc['pend'][i]['w2'] for i in ids]),
                          q25_w1_r0=sorted(w['pend'])[len(ids) // 4], q75_w1_r0=sorted(w['pend'])[3 * len(ids) // 4],
                          vals_r0=w['pend'], vals_dRL=dRL, vals_dPT=dPT)
        # B defined on x1 (independent draw) for robustness of r0 w1
        idsx1 = [f'ev:{n}' for n in sorted(Bx1) if f'ev:{n}' in sc['pend']]
        row['B_ev_x1def_w1_r0'] = med([sc['pend'][i]['w1'] for i in idsx1]) if idsx1 else None
        row['B_ev_x1def_n'] = len(idsx1)
        # cross-seed (selection-free) eventual proofs of OTHER seeds of the same organism, on this seed's B
        xdir = (RUNS['cap6'] + f'/score/rev12_s{s}') if run == 'cap12' else (RUNS['cap6'] + f'/score/cross_s{s}')
        pre = 'ev12s' if run == 'cap12' else 'ev6s'
        xs = {ck: score(f'{xdir}/s{s}_{ck}.jsonl') for ck in ('p1600', 'pend', 'r8')}
        def per_thm(ck, prefixes):
            v = {}
            for n in B:
                xsv = [xs[ck][f'{p}:{n}']['w1'] for p in prefixes if f'{p}:{n}' in xs[ck]]
                if xsv: v[n] = st.mean(xsv)
            return v
        others = [f'{pre}{t}' for t in (0, 1, 2) if t != s]
        for lab, prefs in (('B_xseed', others), ('B_own_via_xdir', [f'{pre}{s}']),
                           ('B_otherorg', [('ev6s' if run == 'cap12' else 'ev12s') + str(t) for t in (0, 1, 2)])):
            v = {ck: per_thm(ck, prefs) for ck in xs}
            common = sorted(set(v['p1600']) & set(v['pend']) & set(v['r8']))
            if common:
                a, b, c = ([v[ck][n] for n in common] for ck in ('p1600', 'pend', 'r8'))
                row[lab] = dict(n=len(common), w1_r0=med(b), w1_r8=med(c), dRL=med(c) - med(b), dPT=med(b) - med(a),
                                dd=(med(c) - med(b)) - (med(b) - med(a)))
        # replay-only control of pend (cap12 only): B references under the control vs r0 and r8
        if run == 'cap12':
            cp = score(HOME + f'/work/rl-from-ckpt/artifacts/rfc/score/cpend_s{s}/s{s}_pend_c8.jsonl')
            ids = [f'ref:{n}' for n in sorted(B) if f'ref:{n}' in cp and f'ref:{n}' in sc['pend']]
            row['B_ref_ctrl'] = dict(n=len(ids), w1_r0=med([sc['pend'][i]['w1'] for i in ids]), w1_ctrl=med([cp[i]['w1'] for i in ids]),
                                     w1_r8=med([sc['r8'][i]['w1'] for i in ids]))
        res[(run, s)] = row
        e, r_, c = row['B_ev'], row['B_ref'], row['C_ref']
        print(f"s{s} A/B/C {row['A']}/{row['B']}/{row['C']} | B(x0) solved by r0 x1: {row['B_x0_solved_by_r0_x1']}")
        for lab in ('B_ev', 'B_ref', 'C_ref', 'A_ev'):
            q = row[lab]
            print(f"  {lab:6s} n{q['n']:4d} w1 p1600 {q['w1_1600']:7.2f} r0 {q['w1_r0']:7.2f} (IQR {q['q25_w1_r0']:.2f}..{q['q75_w1_r0']:.2f}) r8 {q['w1_r8']:6.2f} "
                  f"dRL {q['dRL']:5.2f} dPT {q['dPT']:5.2f} dd {q['dd']:5.2f} | r0: w1<ln(1/400) {q['frac_w1_lt_ln400_r0']:.2f} w2<-4 {q['frac_w2_lt_m4_r0']:.2f} "
                  f"w2<ln(1/400) {q['frac_w2_lt_ln400_r0']:.2f} med w2 {q['med_w2_r0']:.2f} | paired med dRL {q['pdRL']:.2f} dPT {q['pdPT']:.2f}")
        for lab in ('B_xseed', 'B_own_via_xdir', 'B_otherorg'):
            if lab in row:
                q = row[lab]; print(f"  {lab:14s} n{q['n']:4d} w1 r0 {q['w1_r0']:7.2f} r8 {q['w1_r8']:6.2f} dRL {q['dRL']:5.2f} dPT {q['dPT']:5.2f} dd {q['dd']:5.2f}")
        print(f"  B_ev with B from x1 draw: n {row['B_ev_x1def_n']} w1 r0 {row['B_ev_x1def_w1_r0']:.2f}")
        if 'B_ref_ctrl' in row: print('  B_ref r0 / replay-ctrl / r8 w1:', {k: round(v, 2) for k, v in row['B_ref_ctrl'].items()})

print('\n===== pooled / seed-level summaries =====')
for run in ('cap12', 'cap6'):
    for lab in ('B_ev', 'B_ref'):
        pooled = [x for s in (0, 1, 2) for x in res[(run, s)][lab]['vals_r0']]
        m = med(pooled)
        per = [res[(run, s)][lab]['w1_r0'] for s in (0, 1, 2)]
        print(f"{run} {lab} w1 at r0: pooled median {m:.2f} -> 1 in {math.exp(-m):.0f}; per-seed medians {[round(x,2) for x in per]} -> 1 in "
              f"{[round(math.exp(-x)) for x in per]}; mean-of-seed {st.mean(per):.2f} -> 1 in {math.exp(-st.mean(per)):.0f}")
    pooledC = [x for s in (0, 1, 2) for x in res[(run, s)]['C_ref']['vals_r0']]
    print(f"{run} C_ref w1 r0 pooled median {med(pooledC):.2f}; frac w2<-4 per seed {[round(res[(run,s)]['C_ref']['frac_w2_lt_m4_r0'],2) for s in (0,1,2)]}"
          f"; B_ev frac w2<-4 {[round(res[(run,s)]['B_ev']['frac_w2_lt_m4_r0'],2) for s in (0,1,2)]}; B_ref {[round(res[(run,s)]['B_ref']['frac_w2_lt_m4_r0'],2) for s in (0,1,2)]}")
# seed-level contrast cap6 vs cap12 on dd (median dRL - median dPT)
def welch(a, b):
    ma, mb, va, vb = st.mean(a), st.mean(b), st.variance(a), st.variance(b)
    se = math.sqrt(va / len(a) + vb / len(b)); t = (ma - mb) / se
    df = (va / len(a) + vb / len(b)) ** 2 / ((va / len(a)) ** 2 / (len(a) - 1) + (vb / len(b)) ** 2 / (len(b) - 1))
    return ma - mb, se, t, df
for lab in ('B_ev', 'B_ref', 'B_xseed'):
    a = [res[('cap6', s)][lab]['dd'] for s in (0, 1, 2)]; b = [res[('cap12', s)][lab]['dd'] for s in (0, 1, 2)]
    d, se, t, df = welch(a, b)
    print(f"dd {lab}: cap6 {[round(x,2) for x in a]} sd {st.stdev(a):.2f} | cap12 {[round(x,2) for x in b]} sd {st.stdev(b):.2f} | diff {d:.2f} se {se:.2f} t {t:.1f} df {df:.1f}"
          f" | min(cap6) - max(cap12) {min(a)-max(b):.2f}")
# within-seed bootstrap CI of dd per seed (B_ev), cap12, to show per-seed resolution
for run in ('cap12', 'cap6'):
    for s in (0, 1, 2):
        q = res[(run, s)]['B_ev']; rng = random.Random(s); n = len(q['vals_dRL']); bs = []
        idx = list(range(n))
        for _ in range(2000):
            ii = [rng.choice(idx) for _ in idx]; bs.append(med([q['vals_dRL'][i] for i in ii]) - med([q['vals_dPT'][i] for i in ii]))
        bs.sort(); print(f"{run} s{s} B_ev dd {q['dd']:.2f} theorem-bootstrap 95% [{bs[50]:.2f}, {bs[1949]:.2f}]")
json.dump({f'{k[0]}_s{k[1]}': {kk: ({a: b for a, b in vv.items() if not a.startswith('vals')} if isinstance(vv, dict) else vv) for kk, vv in v.items()}
           for k, v in res.items()}, open(OUT + 'c5_trajectory.json', 'w'), indent=1)

for run in ('cap12','cap6'):
    for lab in ('B_ev','B_ref'):
        a=[res[(run,s)][lab]['pdRL']-res[(run,s)][lab]['pdPT'] for s in (0,1,2)]
        print(f"{run} {lab} median(paired dRL) - median(paired dPT) per seed {[round(x,2) for x in a]} mean {st.mean(a):.2f} sd {st.stdev(a):.2f}")
# total vs worst step at r0 for B eventual (is the rest of the proof ~free?)
for run in ('cap12', 'cap6'):
    for s in (0, 1, 2):
        A, B, C = groups(run, s); sc = score(f'{RUNS[run]}/score/s{s}/s{s}_pend.jsonl')
        ids = [f'ev:{n}' for n in B if f'ev:{n}' in sc]
        tot = [sc[i]['tot'] for i in ids]; rest = [sc[i]['tot'] - sc[i]['w1'] for i in ids]
        print(f"{run} s{s} B_ev r0 total median {med(tot):.2f}  total-minus-w1 median {med(rest):.2f}  w1+w2 share of total {med([(sc[i]['w1']+sc[i]['w2'])/sc[i]['tot'] for i in ids]):.2f}")
# matched theorems: B at cap6 seed s AND B at cap12 seed s (same theorem set for both organisms), own eventual + reference
print('\nmatched B6∩B12 per seed index (paired medians of per-theorem deltas):')
for s in (0, 1, 2):
    B6 = groups('cap6', s)[1]; B12 = groups('cap12', s)[1]; M = sorted(B6 & B12)
    for kind in ('ev', 'ref'):
        out = []
        for run in ('cap6', 'cap12'):
            sc = {ck: score(f'{RUNS[run]}/score/s{s}/s{s}_{ck}.jsonl') for ck in ('p1600', 'pend', 'r8')}
            ids = [f'{kind}:{n}' for n in M if all(f'{kind}:{n}' in sc[c] for c in sc)]
            dRL = [sc['r8'][i]['w1'] - sc['pend'][i]['w1'] for i in ids]; dPT = [sc['pend'][i]['w1'] - sc['p1600'][i]['w1'] for i in ids]
            out.append(f"{run} n{len(ids)} r0 {med([sc['pend'][i]['w1'] for i in ids]):.2f} dRL {med(dRL):.2f} dPT {med(dPT):.2f} dd {med(dRL)-med(dPT):.2f}")
        print(f'  s{s} |B6∩B12|={len(M)} {kind}: ' + ' || '.join(out))
