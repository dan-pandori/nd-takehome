#!/usr/bin/env python3
"""Reviewer (trajectory-cap6): pre-registered quantities from the per-step score files (T1.0 step_lp), my own
summaries; cap-6 groups from rv6/recount.json (my recount), cap-12 groups recounted here from trajectory's eval files
(bucket copy in ~/review/trajectory/artifacts/tj)."""
import json, os, statistics as st, random, collections
from recount import load, CK
R = os.path.expanduser('~/review/trajectory-cap6'); S = f'{R}/artifacts/tj6/score'
T12 = os.path.expanduser('~/review/trajectory/artifacts/tj')
med = st.median; rd = lambda f: [json.loads(l) for l in open(f) if l.strip()]
G6 = json.load(open(f'{R}/rv6/recount.json'))['groups']
def pool(n): return 'tb72' if n.startswith('textbook_') else 'h250'
# cap-12 groups from trajectory's x0 reads
G12 = {}
for s in (0, 1, 2):
    g = {}
    for p in ('tb72', 'h250'):
        r0 = load(s, 'pend', p, 0, E=f'{T12}/eval'); r8 = load(s, 'r8', p, 0, E=f'{T12}/eval')
        for n in r0: g[f'{p}:{n}'] = 'A' if r0[n]['proofs'] else ('B' if r8[n]['proofs'] else 'C')
    G12[str(s)] = g
print('cap-12 groups', {s: dict(collections.Counter(g.values())) for s, g in G12.items()})
def maj(G, lab): return {k for k in G['0'] if sum(G[s][k] == lab for s in '012') >= 2}
A12, B12, C12, A6, B6, C6 = maj(G12, 'A'), maj(G12, 'B'), maj(G12, 'C'), maj(G6, 'A'), maj(G6, 'B'), maj(G6, 'C')
print(f'majority sets: A6 {len(A6)} B6 {len(B6)} C6 {len(C6)} | A12 {len(A12)} B12 {len(B12)} C12 {len(C12)} | B6&A12 {len(B6 & A12)} A6&A12 {len(A6 & A12)} B6&B12 {len(B6 & B12)} C6&A12 {len(C6&A12)}')
def scores(d, cks=CK, pre=None):
    return {ck: {r['tid']: r['T1.0']['step_lp'] for r in rd(f'{d}/{pre}_{ck}.jsonl')} for ck in cks}
w1 = min
out = {}
def boot(per, f=med, n=2000, rng=random.Random(0)):
    v = sorted(st.mean(f([rng.choice(L) for _ in L]) for L in per) for _ in range(n)); return v[int(.025*n)], v[int(.975*n)]
SC, TG, CR = {}, {}, {}
for s in (0, 1, 2):
    SC[s] = scores(f'{S}/s{s}', pre=f's{s}'); TG[s] = {r['tid']: r for r in rd(f'{S}/s{s}/targets.jsonl')}
    CR[s] = scores(f'{S}/cross_s{s}', pre=f's{s}')
    assert all(set(SC[s][ck]) == set(TG[s]) for ck in CK)
CT = {r['tid']: r for r in rd(f'{R}/data/tj6/cross.jsonl')}
# --- item 3: headline on own eventual, reference, cross-seed
def contrast(s, tids, sc):
    dRL = [w1(sc['r8'][t]) - w1(sc['pend'][t]) for t in tids]; dPT = [w1(sc['pend'][t]) - w1(sc['p1600'][t]) for t in tids]
    return dict(n=len(tids), w1_p1600=med([w1(sc['p1600'][t]) for t in tids]), w1_r0=med([w1(sc['pend'][t]) for t in tids]),
                w1_r8=med([w1(sc['r8'][t]) for t in tids]), dRL=med(dRL), dPT=med(dPT),
                paired=med([a - b for a, b in zip(dRL, dPT)]), _dRL=dRL, _dPT=dPT)
H = collections.defaultdict(dict)
for s in (0, 1, 2):
    g = G6[str(s)]
    B = [f'ev:{k.split(":",1)[1]}' for k, v in g.items() if v == 'B']
    Bref = [f'ref:{k.split(":",1)[1]}' for k, v in g.items() if v == 'B' and f'ref:{k.split(":",1)[1]}' in TG[s]]
    Bx = [t for t in CR[s]['pend'] if t.startswith('ev6s') and not t.startswith(f'ev6s{s}:') and g[f'{pool(t.split(":",1)[1])}:{t.split(":",1)[1]}'] == 'B']
    assert all(t in SC[s]['pend'] for t in B)
    H['own'][s] = contrast(s, B, SC[s]); H['ref'][s] = contrast(s, Bref, SC[s]); H['cross'][s] = contrast(s, Bx, CR[s])
    A = [f'ev:{k.split(":",1)[1]}' for k, v in g.items() if v == 'A' and f'ev:{k.split(":",1)[1]}' in SC[s]['pend']]
    H['ownA'][s] = contrast(s, A, SC[s])
for kind in ('own', 'ref', 'cross', 'ownA'):
    hs = H[kind]
    print(f'--- item 3, B {kind}' if kind != 'ownA' else '--- A own')
    for s in (0, 1, 2):
        h = hs[s]; print(f'  s{s}: n {h["n"]} w1 p1600 {h["w1_p1600"]:.2f} r0 {h["w1_r0"]:.2f} r8 {h["w1_r8"]:.2f}  dRL {h["dRL"]:.2f} dPT {h["dPT"]:.2f}  dRL>dPT {h["dRL"] > h["dPT"]}  paired med {h["paired"]:.2f}')
    diff = [hs[s]['dRL'] - hs[s]['dPT'] for s in (0, 1, 2)]
    # bootstrap of (med dRL - med dPT), theorems resampled within seed, paired
    rng = random.Random(1); bs = []
    for _ in range(2000):
        v = []
        for s in (0, 1, 2):
            idx = [rng.randrange(hs[s]['n']) for _ in range(hs[s]['n'])]
            v.append(med([hs[s]['_dRL'][i] for i in idx]) - med([hs[s]['_dPT'][i] for i in idx]))
        bs.append(st.mean(v))
    bs.sort()
    print(f'  med dRL - med dPT per seed {[round(x,2) for x in diff]}  IQM(=mean) {st.mean(diff):.2f} [{bs[50]:.2f}, {bs[1949]:.2f}]  dRL>dPT in {sum(x > 0 for x in diff)}/3; '
          f'IQM dRL {st.mean(hs[s]["dRL"] for s in (0,1,2)):.2f} dPT {st.mean(hs[s]["dPT"] for s in (0,1,2)):.2f}')
    out[f'item3_{kind}'] = {s: {k: v for k, v in hs[s].items() if not k.startswith('_')} for s in (0, 1, 2)}
    out[f'item3_{kind}_diff'] = dict(per_seed=diff, iqm=st.mean(diff), ci=[bs[50], bs[1949]])
# --- item 5 totals; item 6 C refs
for s in (0, 1, 2):
    g = G6[str(s)]; ev = collections.defaultdict(list); ref = collections.defaultdict(list)
    for k, v in g.items():
        n = k.split(':', 1)[1]
        if f'ev:{n}' in TG[s]: ev[v].append(f'ev:{n}')
        if f'ref:{n}' in TG[s]: ref[v].append(f'ref:{n}')
    tot = {f'{G}_{ck}': med([sum(SC[s][ck][t]) for t in ev[G]]) for G in 'AB' for ck in ('pend', 'r8')}
    C = ref['C']
    cw = {ck: med([w1(SC[s][ck][t]) for t in C]) for ck in ['pend'] + [f'r{i}' for i in range(1, 9)]}
    cd = med([w1(SC[s]['r8'][t]) - w1(SC[s]['pend'][t]) for t in C])
    print(f's{s} item5 totals {({k: round(v, 2) for k, v in tot.items()})}  | item6 C ref n {len(C)} (of C {sum(v=="C" for v in g.values())}) med w1 r0..r8 {[round(x,2) for x in cw.values()]} max {max(cw.values()):.2f} dRL {cd:.2f}')
    out[f'item5_s{s}'] = tot; out[f'item6_s{s}'] = dict(n=len(C), w1=cw, dRL=cd)
    out[f'nref_s{s}'] = {G: len(v) for G, v in ref.items()}; out[f'nev_s{s}'] = {G: len(v) for G, v in ev.items()}
# --- item 4 (cap 6 vs cap 12), pooled (theorem, seed) pairs
SC12 = {k: scores(f'{T12}/score/s{k}', cks=['p1600', 'pend', 'r8'], pre=f's{k}') for k in (0, 1, 2)}
TG12 = {k: {r['tid']: r for r in rd(f'{T12}/score/s{k}/targets.jsonl')} for k in (0, 1, 2)}
def nm(k): return k.split(':', 1)[1]
a_B = [TG[s][f'ev:{nm(k)}']['n_steps'] for s in (0,1,2) for k in B6 & A12 if f'ev:{nm(k)}' in TG[s]]
a_A = [TG[s][f'ev:{nm(k)}']['n_steps'] for s in (0,1,2) for k in A6 & A12 if f'ev:{nm(k)}' in TG[s]]
print(f'4a: action count cap-6 eventual, B6&A12 med {med(a_B)} (n {len(a_B)}) vs A6&A12 med {med(a_A)} (n {len(a_A)}); diff {med(a_B)-med(a_A)} (pred >= 2)')
# 4b: cap-12 eventual proof under cap-6 pend (cross_s{s}, tids ev12s{k}) vs under cap-12 pend (trajectory s{k} ev:)
u6 = [w1(CR[s]['pend'][f'ev12s{k}:{nm(t)}']) for s in (0,1,2) for k in (0,1,2) for t in B6 & A12 if f'ev12s{k}:{nm(t)}' in CR[s]['pend']]
u6r8 = [w1(CR[s]['r8'][f'ev12s{k}:{nm(t)}']) for s in (0,1,2) for k in (0,1,2) for t in B6 & A12 if f'ev12s{k}:{nm(t)}' in CR[s]['pend']]
u12 = [w1(SC12[k]['pend'][f'ev:{nm(t)}']) for k in (0,1,2) for t in B6 & A12 if f'ev:{nm(t)}' in SC12[k]['pend']]
print(f'4b: cap-12 eventual on B6&A12: med w1 under cap-6 pend {med(u6):.2f} (n {len(u6)} pairs, pred <= -4); under cap-12 pend {med(u12):.2f} (n {len(u12)}, pred >= -3)')
# per-seed version (cap-6 seed s scoring cap-12 seed s's proofs)
print('    per cap-6 seed s (all 3 cap-12 seeds\' proofs):', [round(med([w1(CR[s]['pend'][f'ev12s{k}:{nm(t)}']) for k in (0,1,2) for t in B6 & A12 if f'ev12s{k}:{nm(t)}' in CR[s]['pend']]), 2) for s in (0,1,2)])
# 4c: index (1-based) of worst step of own eventual under cap-6 pend
idx = [SC[s]['pend'][f'ev:{nm(t)}'].index(w1(SC[s]['pend'][f'ev:{nm(t)}'])) + 1 for s in (0,1,2) for t in B6 & A12 if f'ev:{nm(t)}' in SC[s]['pend']]
print(f'4c: worst-step index >= 7 in {sum(i >= 7 for i in idx)}/{len(idx)} = {sum(i >= 7 for i in idx)/len(idx):.2f} (pred >= 0.5); median index {med(idx)}')
# also restrict to proofs with >= 7 actions
# 4d
print(f'4d: cap-12 eventual under cap-6 r8 med w1 {med(u6r8):.2f} vs pend {med(u6):.2f}: diff of medians {med(u6r8)-med(u6):.2f}; paired median {med([a-b for a,b in zip(u6r8,u6)]):.2f} (pred >= 2)')
# 4e
e = [w1(SC12[k]['pend'][f'ev:{nm(t)}']) - w1(SC12[k]['p1600'][f'ev:{nm(t)}']) for k in (0,1,2) for t in B6 & A12 if f'ev:{nm(t)}' in SC12[k]['pend']]
e1 = med([w1(SC12[k]['pend'][f'ev:{nm(t)}']) for k in (0,1,2) for t in B6 & A12 if f'ev:{nm(t)}' in SC12[k]['pend']]) - med([w1(SC12[k]['p1600'][f'ev:{nm(t)}']) for k in (0,1,2) for t in B6 & A12 if f'ev:{nm(t)}' in SC12[k]['pend']])
print(f'4e: cap-12 own eventual on B6&A12, w1 pend - p1600: paired median {med(e):.2f}, diff of medians {e1:.2f} (n {len(e)}; pred >= 3)')
out['item4'] = dict(nB6A12=len(B6 & A12), a=[med(a_B), med(a_A)], b=[med(u6), med(u12)], c=sum(i >= 7 for i in idx)/len(idx), d=[med(u6r8), med(u6)], e=med(e))
out['sets'] = {k: sorted(v) for k, v in dict(A6=A6, B6=B6, C6=C6, A12=A12, B12=B12, C12=C12).items()}
# --- consistency: cross targets == eventual files; rev12 under cap-12 seed K == trajectory's own scores
evs = {k: {f'ev6s{k}:{r["name"]}': r['proof'] for r in rd(f'{R}/artifacts/tj6/targets/eventual_s{k}.jsonl')} for k in (0,1,2)}
ev12 = {k: {f'ev12s{k}:{r["name"]}': r['proof'] for r in rd(f'{T12}/targets/eventual_s{k}.jsonl')} for k in (0,1,2)}
ok6 = all(CT[t]['proof'] == p for k in evs for t, p in evs[k].items()) and sum(map(len, evs.values())) == sum(1 for t in CT if t.startswith('ev6'))
ok12 = all(CT[t]['proof'] == p for k in ev12 for t, p in ev12[k].items()) and sum(map(len, ev12.values())) == sum(1 for t in CT if t.startswith('ev12'))
print('cross.jsonl == cap-6 eventual files:', ok6, ' == trajectory eventual files:', ok12)
mx = 0; n = 0
for K in (0, 1, 2):
    rv = scores(f'{S}/rev12_s{K}', cks=['p1600', 'pend', 'r8'], pre=f's{K}')
    for ck in ('p1600', 'pend', 'r8'):
        for t, v in rv[ck].items():
            if t.startswith(f'ev12s{K}:'):
                o = SC12[K][ck].get('ev:' + nm(t))
                if o is not None: mx = max(mx, max(abs(a - b) for a, b in zip(v, o))); n += 1
print(f'rev12 (cap-12 ckpts) re-scores of trajectory\'s own eventual proofs vs trajectory\'s scores: n {n}, max |step diff| {mx}')
json.dump(out, open(f'{R}/rv6/analysis.json', 'w'), indent=1, default=str)
