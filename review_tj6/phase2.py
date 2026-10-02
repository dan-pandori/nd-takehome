#!/usr/bin/env python3
"""Reviewer phase 2: recompute the write-up's numbers my phase 1 did not cover."""
import json, os, statistics as st, collections, random
from recount import load, CK
R = os.path.expanduser('~/review/trajectory-cap6'); S = f'{R}/artifacts/tj6/score'; T12 = os.path.expanduser('~/review/trajectory/artifacts/tj')
rd = lambda f: [json.loads(l) for l in open(f) if l.strip()]; med = st.median
G6 = json.load(open(f'{R}/rv6/recount.json'))['groups']; sets = json.load(open(f'{R}/rv6/analysis.json'))['sets']
pool = lambda n: 'tb72' if n.startswith('textbook_') else 'h250'; nm = lambda t: t.split(':', 1)[1]
def sc(d, pre, cks=CK): return {ck: {r['tid']: r['T1.0']['step_lp'] for r in rd(f'{d}/{pre}_{ck}.jsonl')} for ck in cks}
SC = {s: sc(f'{S}/s{s}', f's{s}') for s in (0, 1, 2)}; CR = {s: sc(f'{S}/cross_s{s}', f's{s}') for s in (0, 1, 2)}
grp = lambda s, n: G6[str(s)][f'{pool(n)}:{n}']
# pooled medians (key checkpoints)
for lab, kind, G in (('A ev', 'ev', 'A'), ('B ev', 'ev', 'B'), ('B ref', 'ref', 'B'), ('C ref', 'ref', 'C')):
    row = []
    for ck in ('p0', 'p12000', 'pend', 'r1', 'r4', 'r8'):
        row.append(med([min(SC[s][ck][t]) for s in (0,1,2) for t in SC[s][ck] if t.startswith(kind + ':') and grp(s, nm(t)) == G]))
    print(f'pooled w1 {lab}:', [round(x, 2) for x in row])
print('pooled B ev total:', [round(med([sum(SC[s][ck][t]) for s in (0,1,2) for t in SC[s][ck] if t.startswith('ev:') and grp(s, nm(t)) == 'B']), 2) for ck in ('p0','p12000','pend','r1','r4','r8')])
# cross-seed variants and cap-12 eventual on B
def contrast(pairs):  # pairs: list of (s, tid) in CR
    out = []
    for s in (0, 1, 2):
        P = [t for ss, t in pairs if ss == s]
        dRL = [min(CR[s]['r8'][t]) - min(CR[s]['pend'][t]) for t in P]; dPT = [min(CR[s]['pend'][t]) - min(CR[s]['p1600'][t]) for t in P]
        out.append((len(P), med([min(CR[s]['pend'][t]) for t in P]), med([min(CR[s]['r8'][t]) for t in P]), med(dRL), med(dPT), med([a - b for a, b in zip(dRL, dPT)])))
    return out
def show(lab, o):
    print(lab, ' '.join(f'[n{n} pend {a:.2f} r8 {b:.2f} dRL {c:.2f} dPT {d:.2f} paired {e:.2f}]' for n, a, b, c, d, e in o),
          f'| IQM dRL {st.mean(x[3] for x in o):.2f} dPT {st.mean(x[4] for x in o):.2f} paired {st.mean(x[5] for x in o):.2f}')
# (i) B of scoring seed (my phase-1 definition)
show('cross, B of scoring seed:', contrast([(s, t) for s in (0,1,2) for t in CR[s]['pend'] if t.startswith('ev6s') and not t.startswith(f'ev6s{s}:') and grp(s, nm(t)) == 'B']))
# (ii) B of the proof's seed
show('cross, B of proof seed:  ', contrast([(s, t) for s in (0,1,2) for t in CR[s]['pend'] if t.startswith('ev6s') and not t.startswith(f'ev6s{s}:') and grp(int(t[4]), nm(t)) == 'B']))
# (iii) B of both
show('cross, B of both:        ', contrast([(s, t) for s in (0,1,2) for t in CR[s]['pend'] if t.startswith('ev6s') and not t.startswith(f'ev6s{s}:') and grp(int(t[4]), nm(t)) == 'B' and grp(s, nm(t)) == 'B']))
show('cap-12 eventual on B (scoring seed):', contrast([(s, t) for s in (0,1,2) for t in CR[s]['pend'] if t.startswith('ev12') and grp(s, nm(t)) == 'B']))
# late pretraining B and A
for G in 'AB':
    v = [med([min(SC[s]['pend'][t]) - min(SC[s]['p8000'][t]) for t in SC[s]['pend'] if t.startswith('ev:') and grp(s, nm(t)) == G]) for s in (0,1,2)]
    print(f'late PT p8000->pend {G} eventual w1:', [round(x, 2) for x in v], 'mean', round(st.mean(v), 2))
# B6&A12 descriptive: own eventual pend -> r8; cap-6 cross-seed proofs under r8; cap-6 eventual under cap-12 pend; refs
BA = set(sets['B6']) & set(sets['A12'])
own = [(min(SC[s]['pend'][f'ev:{nm(k)}']), min(SC[s]['r8'][f'ev:{nm(k)}'])) for s in (0,1,2) for k in BA if f'ev:{nm(k)}' in SC[s]['pend']]
print(f'B6&A12 own eventual pend {med([a for a,b in own]):.2f} -> r8 {med([b for a,b in own]):.2f} (n {len(own)})')
xs = [min(CR[s]['r8'][t]) for s in (0,1,2) for t in CR[s]['r8'] if t.startswith('ev6s') and not t.startswith(f'ev6s{s}:') and f'{pool(nm(t))}:{nm(t)}' in BA]
x12 = [min(CR[s]['r8'][t]) for s in (0,1,2) for t in CR[s]['r8'] if t.startswith('ev12') and f'{pool(nm(t))}:{nm(t)}' in BA]
xs0 = [min(CR[s]['pend'][t]) for s in (0,1,2) for t in CR[s]['r8'] if t.startswith('ev6s') and not t.startswith(f'ev6s{s}:') and f'{pool(nm(t))}:{nm(t)}' in BA]
print(f'B6&A12 under cap-6 r8: other-seed cap-6 eventual {med(xs):.2f} (n {len(xs)}; pend {med(xs0):.2f}) vs cap-12 eventual {med(x12):.2f} (n {len(x12)})')
RV = {K: sc(f'{S}/rev12_s{K}', f's{K}', cks=['pend']) for K in (0,1,2)}
v = [min(RV[K]['pend'][t]) for K in (0,1,2) for t in RV[K]['pend'] if t.startswith('ev6') and f'{pool(nm(t))}:{nm(t)}' in BA]
print(f'B6&A12 cap-6 eventual under cap-12 pend: {med(v):.2f} (n {len(v)})')
SC12 = {k: sc(f'{T12}/score/s{k}', f's{k}', cks=['pend']) for k in (0,1,2)}
r6 = [min(SC[s]['pend'][f'ref:{nm(k)}']) for s in (0,1,2) for k in BA if f'ref:{nm(k)}' in SC[s]['pend']]
r12 = [min(SC12[k]['pend'][f'ref:{nm(t)}']) for k in (0,1,2) for t in BA if f'ref:{nm(t)}' in SC12[k]['pend']]
print(f'B6&A12 ref w1 cap-6 pend {med(r6):.2f} (n {len(r6)}) cap-12 pend {med(r12):.2f} (n {len(r12)})')
# truncation: RL strata > 0.1 %
tr = json.load(open(f'{R}/rv6/recount.json'))['trunc']
rl = [(k, g, v) for k, d in tr.items() for g, v in d.items() if ':' in g and '_r' in k]
print('RL strata > 0.1 %:', sum(v > 0.001 for _, _, v in rl), 'of', len(rl))
cd = json.load(open(f'{R}/rv6/capdiag.json'))
print('2x C@r8 residual cut-off (mean over seed x pool):', round(100 * st.mean(v['cut2x'] for k, v in cd.items() if '_r8_' in k), 2), '%')
# example theorem
for t in SC[0]['pend']:
    if t.startswith('ev:'):
        r = [x for x in rd(f'{R}/artifacts/tj6/targets/targets_s0.jsonl') if x['tid'] == t][0]
        if r['prompt'] == 'THM ( ( Q v ( Q > R ) ) & ( ~ ( R & S ) ) ) SEQ ( ~ ( ( Q v ( Q > R ) ) > ( R & S ) ) ) PRF':
            print('example', t, grp(0, nm(t)), f'{pool(nm(t))}:{nm(t)}' in BA, {ck: [round(x, 2) for x in SC[0][ck][t]] for ck in ('pend', 'r1', 'r4', 'r8')}); print(r['proof'])
# executor's aggregation: per theorem, mean over the theorem's fixed proofs; then median over B theorems per seed
for lab, pre in (('cross-seed', 'ev6s'), ('cap-12', 'ev12s')):
    per = {k: [] for k in ('pend', 'r8', 'dRL', 'dPT', 'paired')}
    for s in (0, 1, 2):
        acc = collections.defaultdict(lambda: collections.defaultdict(list))
        for t in CR[s]['pend']:
            if t.startswith(pre) and not t.startswith(f'ev6s{s}:') and grp(s, nm(t)) == 'B':
                a, b, c = min(CR[s]['p1600'][t]), min(CR[s]['pend'][t]), min(CR[s]['r8'][t])
                for k, v in (('pend', b), ('r8', c), ('dRL', c - b), ('dPT', b - a), ('paired', (c - b) - (b - a))): acc[nm(t)][k].append(v)
        for k in per: per[k].append(med([st.mean(d[k]) for d in acc.values()]))
    print(f'{lab} (per-theorem mean):', {k: [round(x, 2) for x in v] + [round(st.mean(v), 2)] for k, v in per.items()})
