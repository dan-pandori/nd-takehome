"""Reviewer's independent recount for frontier-supply (phase 1). Reads raw read-out rows only."""
import json, os, random, statistics as S, collections
RR = os.path.expanduser('~/review/frontier-supply/artifacts/fsup/rr')
def rows(tag, pool):
    fn = f'{RR}/{tag}__{pool}.jsonl'
    return [json.loads(l) for l in open(fn)] if os.path.exists(fn) else None
lenof = {}
for l in open(os.path.expanduser('~/review/frontier-supply/data/fsup/rr600_13_16.jsonl')):
    x = json.loads(l); lenof[x['name']] = x['L_true']
def solved_set(tag):
    out = {}
    lp, rr = rows(tag, 'lp2'), rows(tag, 'rr')
    if lp is not None:
        out['lp2'] = {r['name'] for r in lp if len(r['proofs']) > 0}
        out['lp17'] = {r['name'] for r in lp if r['proofs'] and r['L_true_lb'] == 17}
        out['lp18'] = {r['name'] for r in lp if r['proofs'] and r['L_true_lb'] >= 18}
        assert all(bool(r['proofs']) == r['solved'] for r in lp) and len(lp) == 91
        out['n_lp2_tried'] = {r['n_tried'] for r in lp}
    if rr is not None:
        assert len(rr) == 400
        s = {r['name'] for r in rr if r['proofs']}
        out['rr1516'] = {n for n in s if lenof[n] in (15, 16)}
        out['rr1314'] = {n for n in s if lenof[n] in (13, 14)}
        out['n_rr_tried'] = {r['n_tried'] for r in rr}
    return out
tags = {'C': [f'la_C_s{i}' for i in range(6)], 'S': [f'la_S_s{i}' for i in range(6)], 'R': ['la_R_s0', 'la_R_s1'],
        'B': [f'stage1_s{i}' for i in range(6)]}
res = {a: {t: solved_set(t) for t in ts} for a, ts in tags.items()}
def val(d, q):
    if q == 'primary':
        return len(d['lp2']) + len(d['rr1516']) if 'rr1516' in d and 'lp2' in d else None
    return len(d[q]) if q in d else None
Q = ['primary', 'lp2', 'lp17', 'lp18', 'rr1516', 'rr1314']
print('tag', *Q, 'n_tried', sep='\t')
for a, ts in tags.items():
    for t in ts:
        d = res[a][t]; print(t, *[val(d, q) for q in Q], d.get('n_lp2_tried'), d.get('n_rr_tried'), sep='\t')
def iqm(xs):
    xs = sorted(xs); n = len(xs); lo = n // 4; hi = n - lo
    return S.mean(xs[lo:hi]) if n >= 4 else S.mean(xs)
T = {2: 4.303, 3: 3.182, 4: 2.776, 5: 2.571}; T80 = {2: 1.886, 3: 1.638, 4: 1.533, 5: 1.476}
print()
for q in Q:
    d = [val(res['S'][f'la_S_s{i}'], q) - val(res['C'][f'la_C_s{i}'], q) for i in range(6)]
    rng = random.Random(0); bs = sorted(iqm([rng.choice(d) for _ in d]) for _ in range(20000))
    cc = [val(res['R'][f'la_R_s{i}'], q) - val(res['C'][f'la_C_s{i}'], q) for i in range(2)]
    sdd = (sum(x * x for x in cc) / 2) ** .5
    sdC = S.stdev([val(res['C'][f'la_C_s{i}'], q) for i in range(6)])
    print(f'{q}: S-C per seed {d} mean {S.mean(d):.2f} IQM {iqm(d):.2f} boot95 [{bs[500]:.2f},{bs[19500]:.2f}] '
          f'sd_d(S-C) {S.stdev(d):.2f} paired MDD(sd S-C)={(T[5]+T80[5])*S.stdev(d)/6**.5:.1f}; '
          f"C'-C {cc} sd_d {sdd:.2f} MDD(C'-based)={(T[5]+T80[5])*sdd/6**.5:.1f}; sd(C) {sdC:.2f}")
# per-theorem flips on the primary
def prim(d): return d['lp2'] | d['rr1516']
for i in range(6):
    s, c = prim(res['S'][f'la_S_s{i}']), prim(res['C'][f'la_C_s{i}'])
    print(f's{i}: S-only {len(s-c)} C-only {len(c-s)}', end='')
    if i < 2:
        r = prim(res['R'][f'la_R_s{i}']); print(f"  | C'-only {len(r-c)} C-only(vs C') {len(c-r)}", end='')
    print()
# union / L* on lp2
for a in 'CSR':
    u = set().union(*[prim(res[a][t]) for t in tags[a]])
    print(a, 'union primary', len(u))
b = res['B']
print('base union lp2', len(set().union(*[b[t]['lp2'] for t in tags['B']])), 'base lp2 per seed', [len(b[t]['lp2']) for t in tags['B']])
json.dump({a: {t: {k: sorted(v) for k, v in d.items() if isinstance(v, set) and k.startswith(('lp', 'rr'))} for t, d in ts.items()} for a, ts in res.items()},
          open(os.path.expanduser('~/review/frontier-supply/_rev/solved_sets.json'), 'w'))
