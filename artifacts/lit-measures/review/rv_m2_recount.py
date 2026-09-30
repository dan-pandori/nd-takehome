#!/usr/bin/env python3
"""Reviewer (lit-measures) M2 recount: own depth counter, own per-cell counts, own variance components + bootstrap."""
import json, os, random, statistics as st, itertools, math
R = '/home/dan/review/lit-measures'; D = f'{R}/artifacts/lit-measures/m2'
rd = lambda f: [json.loads(l) for l in open(f)]
H = rd(f'{R}/data/p2/heldout.jsonl')

def box_depth(nd):
    d = 0
    for line in nd.split(' ; '):
        toks = line.split()
        if toks and toks[0] == 'QED': continue
        k = 0
        for t in toks[1:]:
            if t == '|': k += 1
            else: break
        d = max(d, k)
    return d
dep = {r['name']: box_depth(r['proof']) for r in H}
d3 = {n for n, d in dep.items() if d >= 3}
agree = sum((n in d3) == bool(r['pat']['depth3']) for n, r in ((r['name'], r) for r in H))
print(f'own depth counter: {len(d3)} held-out theorems with reference box depth >= 3; agrees with pat.depth3 on {agree}/5000')
from collections import Counter
print('depth hist', sorted(Counter(dep.values()).items()))

def cell(tag):
    fh = f'{D}/heldout_{tag}.jsonl'
    if not os.path.exists(fh): return None
    rows = rd(fh); assert len(rows) == 5000 and len({r['name'] for r in rows}) == 5000
    ok = {r['name']: bool(r['solved']) and len(r['proofs']) > 0 for r in rows}
    assert all(bool(r['solved']) == (len(r['proofs']) > 0) for r in rows)
    m = [x for x in rd(f'{D}/metrics_{tag}.jsonl') if x.get('kind') == 'step']
    args = rd(f'{D}/metrics_{tag}.jsonl')[0]['args']
    return {'overall': sum(ok.values()) / 5000, 'depth3': sum(ok[n] for n in d3) / len(d3), 'val': m[-1]['val2k'],
            'last_step': m[-1]['step'], 'seed': args['seed'], 'data_seed': args['data_seed'], 'impl': args['impl'],
            'data': args['data'], 'steps': args['steps'], 'bs': args['bs'], 'cap': args['cap'], 'mode': args['mode'],
            'solved_rows': [r for r in rows if r['solved']]}
I = range(8); J = range(100, 108)
C = {(i, j): cell(f'i{i}_d{j}') for i in I for j in J}
assert all(C.values()), [k for k, v in C.items() if not v]
for (i, j), c in C.items():
    assert (c['seed'], c['data_seed'], c['impl'], c['data'], c['steps'], c['bs'], c['cap'], c['mode'], c['last_step']) == \
        (i, j, 'fast', 'data/nf/train_p1.jsonl', 6000, 128, 6, 'lean_seq', 6000), (i, j, c)
print('64 cells, recipe checked (fast, lean_seq, cap 6, 6000x128, train_p1, seeds as named)')

def vc(Y):
    """two-way crossed random effects, one obs per cell: E[MS_A] = s2e + b*s2a, E[MS_B] = s2e + a*s2b."""
    a, b = len(Y), len(Y[0]); g = sum(sum(r) for r in Y) / (a * b)
    ra = [sum(r) / b for r in Y]; cb = [sum(Y[x][y] for x in range(a)) / a for y in range(b)]
    ssa = b * sum((m - g) ** 2 for m in ra); ssb = a * sum((m - g) ** 2 for m in cb)
    sst = sum((Y[x][y] - g) ** 2 for x in range(a) for y in range(b)); sse = sst - ssa - ssb
    msa, msb, mse = ssa / (a - 1), ssb / (b - 1), sse / ((a - 1) * (b - 1))
    va, vb = max(0, (msa - mse) / b), max(0, (msb - mse) / a); tot = va + vb + mse
    return dict(init=va / tot, data=vb / tot, resid=mse / tot, msa=msa, msb=msb, mse=mse, F_init=msa / mse, F_data=msb / mse)

def fpval(F, d1, d2):
    # regularised incomplete beta via continued fraction (no scipy on the VPS)
    x = d2 / (d2 + d1 * F); a, b = d2 / 2, d1 / 2
    def betacf(a, b, x):
        qab, qap, qam = a + b, a + 1, a - 1; c, d = 1, 1 - qab * x / qap; d = 1 / d; h = d
        for m in range(1, 300):
            m2 = 2 * m; aa = m * (b - m) * x / ((qam + m2) * (a + m2))
            d = 1 / (1 + aa * d); c = 1 + aa / c; h *= d * c
            aa = -(a + m) * (qab + m) * x / ((a + m2) * (qap + m2))
            d = 1 / (1 + aa * d); c = 1 + aa / c; h *= d * c
        return h
    lbt = math.lgamma(a + b) - math.lgamma(a) - math.lgamma(b) + a * math.log(x) + b * math.log(1 - x)
    return math.exp(lbt) * betacf(a, b, x) / a if x < (a + 1) / (a + b + 2) else 1 - math.exp(lbt) * betacf(b, a, 1 - x) / b

out = {}
for q in ('depth3', 'overall', 'val'):
    Y = [[C[(i, j)][q] for j in J] for i in I]; flat = [v for r in Y for v in r]
    v = vc(Y)
    rng = random.Random(12345); bs = {k: [] for k in ('init', 'data', 'resid')}
    for _ in range(4000):
        ri = [rng.randrange(8) for _ in I]; cj = [rng.randrange(8) for _ in J]
        Z = [[Y[x][y] for y in cj] for x in ri]
        try: w = vc(Z)
        except ZeroDivisionError: continue
        for k in bs: bs[k].append(w[k])
    ci = {k: (sorted(x)[int(0.025 * len(x))], sorted(x)[int(0.975 * len(x)) - 1]) for k, x in bs.items()}
    pi, pd = fpval(v['F_init'], 7, 49), fpval(v['F_data'], 7, 49)
    out[q] = dict(v, ci=ci, p_init=pi, p_data=pd, mean=st.mean(flat), sd=st.stdev(flat), lo=min(flat), hi=max(flat))
    print(f"{q:8s} mean {st.mean(flat):.4f} sd {st.stdev(flat):.4f} [{min(flat):.4f},{max(flat):.4f}] "
          f"init {v['init']:.3f} [{ci['init'][0]:.2f},{ci['init'][1]:.2f}] (F {v['F_init']:.2f} p {pi:.3f})  "
          f"data {v['data']:.3f} [{ci['data'][0]:.2f},{ci['data'][1]:.2f}] (F {v['F_data']:.2f} p {pd:.3f})  resid {v['resid']:.3f}")
print('\ndepth-3 grid (rows init 0-7, cols data 100-107):')
for i in I: print(f' i{i} ' + ' '.join(f"{C[(i,j)]['depth3']:.3f}" for j in J))
Hm = [[int(C[(i, j)]['depth3'] >= 0.5) for j in J] for i in I]
print('high mode (>=0.5):', sum(map(sum, Hm)), '/64; rows', [sum(r) for r in Hm], 'cols', [sum(Hm[i][k] for i in I) for k in range(8)])
# row/column concentration: chi-square-like statistic, label permutation
def conc(M):
    rs = [sum(r) for r in M]; cs = [sum(M[i][k] for i in range(8)) for k in range(8)]
    m = sum(rs) / 8; return sum((x - m) ** 2 for x in rs), sum((x - m) ** 2 for x in cs)
o = conc(Hm); flat = [x for r in Hm for x in r]; rng = random.Random(7); ge = [0, 0]; N = 20000
for _ in range(N):
    rng.shuffle(flat); s = conc([flat[k * 8:(k + 1) * 8] for k in range(8)]); ge[0] += s[0] >= o[0] - 1e-9; ge[1] += s[1] >= o[1] - 1e-9
print(f'row concentration p {(ge[0]+1)/(N+1):.4f}, column concentration p {(ge[1]+1)/(N+1):.4f}')
# replicates
reps = {'grid': C[(0, 100)]}
for k in range(1, 9):
    c = cell(f'i0_d100_r{k}')
    if c: assert (c['seed'], c['data_seed']) == (0, 100); reps[f'r{k}'] = c
v3 = [c['depth3'] for c in reps.values()]
print(f"\nreplicates of (i0,d100): n={len(v3)} depth3 {[round(x,3) for x in v3]} sd {st.stdev(v3):.3f}; "
      f"overall sd {st.stdev([c['overall'] for c in reps.values()]):.4f}; val sd {st.stdev([c['val'] for c in reps.values()]):.5f}")
print(f"replicate high-mode count {sum(x>=0.5 for x in v3)}/{len(v3)}")
json.dump({'components': out, 'reps_depth3': v3, 'grid_depth3': [[C[(i, j)]['depth3'] for j in J] for i in I]},
          open(f'{R}/rv/m2_recount.json', 'w'), indent=1, default=str)
# sample for Lean recheck: 100 solved per cell (all 64 + 8 reps), >= half depth-3 where available
rng = random.Random(99); S = []
for tag, c in [(f'i{i}_d{j}', C[(i, j)]) for i in I for j in J] + [(k, v) for k, v in reps.items() if k != 'grid']:
    rows = c['solved_rows']; a = [r for r in rows if r['name'] in d3]; b = [r for r in rows if r['name'] not in d3]
    ka = min(50, len(a)); pick = rng.sample(a, ka) + rng.sample(b, 100 - ka)
    for r in pick:
        S.append({'cell': tag, 'name': r['name'], 'prompt': r['prompt'], 'proof': r['proofs'][0], 'depth3': r['name'] in d3})
with open(f'{R}/rv/m2_lean_sample.jsonl', 'w') as f:
    for s in S: f.write(json.dumps(s) + '\n')
print('Lean sample', len(S))
