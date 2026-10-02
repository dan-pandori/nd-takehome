#!/usr/bin/env python3
"""Reviewer recount for grpo-best (independent of the executor's gb_analysis.py / gb_groups.py).
Reads only per-theorem read-out .jsonl files.  -> review_gb/recount.json + stdout."""
import json, os, math, random, statistics, collections
R = os.path.expanduser('~/review/grpo-best/artifacts/gb')
ARMS = ['default', 'unlikely', 'passk', 'distinct']
SEEDS = [0, 1, 2]
TRUNC = ('action truncated', 'step cap', 'names exhausted')

def load(path):
    out = {}
    for l in open(path):
        r = json.loads(l)
        assert r['name'] not in out
        assert r['n_tried'] - len(r['reasons']) == r['n_ok'], path   # n_ok consistent with per-sample reasons
        out[r['name']] = r
    return out

def read(kind, arm, s, ck, x):
    """322 theorems: tb72 + h250."""
    d = {}
    for p in ('tb72', 'h250'):
        f = f'{R}/ei_eval/s{s}_{ck}__{p}_x{x}.jsonl' if kind == 'ei' else f'{R}/eval/gb_{arm}_s{s}_{ck}__{p}_x{x}.jsonl'
        if not os.path.exists(f):
            return None
        part = load(f)
        assert not set(part) & set(d)
        d.update(part)
    assert len(d) == 322, (kind, arm, s, ck, x, len(d))
    return d

def solved(d): return {n for n, r in d.items() if r['n_ok'] > 0}

def binom_two_sided(a, b):
    n = a + b
    if n == 0: return 1.0
    k = min(a, b)
    p = sum(math.comb(n, i) for i in range(0, k + 1)) / 2 ** n
    return min(1.0, 2 * p)

def iqm(xs):
    xs = sorted(xs); n = len(xs); lo = int(math.floor(n * 0.25)); hi = n - lo
    return statistics.mean(xs[lo:hi])

def boot(xs, B=20000, seed=0):
    rng = random.Random(seed)
    v = sorted(iqm([rng.choice(xs) for _ in xs]) for _ in range(B))
    return [v[int(0.025 * B)], v[int(0.975 * B) - 1]]

out = {'groups': {}, 'cells': [], 'sign': {}, 'trunc': {}}
G = {}
for s in SEEDS:
    pe, r8 = solved(read('ei', None, s, 'pend', 0)), solved(read('ei', None, s, 'r8', 0))
    names = sorted(read('ei', None, s, 'pend', 0))
    G[s] = {n: 'A' if n in pe else 'B' if n in r8 else 'C' for n in names}
    out['groups'][s] = collections.Counter(G[s].values())
print('groups', {s: dict(out['groups'][s]) for s in SEEDS})

def cell(kind, arm, s, ck):
    rows = {}
    for x in (0, 1):
        d = read(kind, arm, s, ck, x)
        if d is None: return None
        rows[x] = d
    g = G[s]
    c = {'kind': kind, 'arm': arm if kind == 'gb' else 'EI', 'seed': s, 'ck': ck}
    for x in (0, 1):
        sv = solved(rows[x])
        c[f'all_x{x}'] = len(sv)
        c[f'tb72_x{x}'] = sum(1 for n in sv if n.startswith('textbook_'))
        for grp in 'ABC':
            ns = [n for n in g if g[n] == grp]
            c[f'{grp}_x{x}'] = sum(1 for n in ns if n in sv)
            c[f'{grp}_p1_x{x}'] = statistics.mean(rows[x][n]['n_ok'] / rows[x][n]['n_tried'] for n in ns) if ns else None
            c[f'{grp}_pk_x{x}'] = c[f'{grp}_x{x}'] / len(ns) if ns else None
        tr = sum(1 for r in rows[x].values() for q in r['reasons'] if any(t in q for t in TRUNC))
        c[f'trunc_x{x}'] = tr / sum(r['n_tried'] for r in rows[x].values())
        # per stratum (reference_lines) max truncation fraction
        st = collections.defaultdict(lambda: [0, 0])
        for r in rows[x].values():
            L = r.get('reference_lines')
            st[L][0] += sum(1 for q in r['reasons'] if any(t in q for t in TRUNC)); st[L][1] += r['n_tried']
        c[f'trunc_maxstratum_x{x}'] = max(a / b for a, b in st.values())
        c[f'n_tried_x{x}'] = sum(r['n_tried'] for r in rows[x].values())
    e = solved(rows[0]) | solved(rows[1])
    c['C_either'] = sum(1 for n in g if g[n] == 'C' and n in e)
    c['all_either'] = len(e)
    c['_solved_either'] = sorted(e)
    return c

for s in SEEDS:
    for ck in ('pend', 'r2', 'r4', 'r8'):
        c = cell('ei', None, s, ck)
        if c: out['cells'].append(c)
    for arm in ARMS:
        for ck in ('r2', 'r4', 'r8'):
            c = cell('gb', arm, s, ck)
            if c: out['cells'].append(c)
# distinct s1 crashed-run r2 read, kept separately
for x in (0, 1):
    pass
def get(arm, s, ck):
    for c in out['cells']:
        if c['arm'] == arm and c['seed'] == s and c['ck'] == ck: return c

print('\n== per cell (C on x1 = headline; all on x1)')
hdr = ['arm', 'seed', 'ck', 'C_x0', 'C_x1', 'C_either', 'B_x1', 'A_x1', 'all_x0', 'all_x1', 'tb72_x0', 'tb72_x1']
print(' '.join(f'{h:>9}' for h in hdr))
for c in out['cells']:
    print(' '.join(f'{str(c[h]):>9}' for h in hdr))

print('\n== headline: C solved at r8, sample seed 1; IQM [95% stratified bootstrap]')
summ = {}
for arm in ['EI'] + ARMS:
    for ck in ('r2', 'r4', 'r8'):
        cs = [get(arm, s, ck) for s in SEEDS]
        if any(c is None for c in cs): continue
        for q in ('C_x1', 'C_either', 'all_x1', 'tb72_x0', 'B_p1_x1', 'B_pk_x1', 'A_p1_x1', 'A_pk_x1', 'C_p1_x1', 'C_pk_x1'):
            v = [c[q] for c in cs]
            summ[f'{arm}|{ck}|{q}'] = {'per_seed': v, 'iqm': iqm(v), 'ci': boot(v)}
for k, v in summ.items():
    if '|r8|' in k or '|r4|' in k:
        print(f'{k:28s} {[round(x, 3) for x in v["per_seed"]]}  IQM {v["iqm"]:.3f} [{v["ci"][0]:.3f}, {v["ci"][1]:.3f}]')
out['summ'] = summ

print('\n== sign test: all 322, GRPO r8 either seed vs EI r8 either seed, pooled over seeds')
for arm in ARMS:
    for ck in ('r8', 'r4', 'r2'):
        a = b = 0; per = []
        ok = True
        for s in SEEDS:
            g, e = get(arm, s, ck), get('EI', s, ck)
            if g is None: ok = False; break
            gs, es = set(g['_solved_either']), set(e['_solved_either'])
            per.append((len(gs - es), len(es - gs))); a += len(gs - es); b += len(es - gs)
        if not ok: continue
        # restricted to C as well
        aC = sum(len([n for n in set(get(arm, s, ck)['_solved_either']) - set(get('EI', s, ck)['_solved_either']) if G[s][n] == 'C']) for s in SEEDS)
        bC = sum(len([n for n in set(get('EI', s, ck)['_solved_either']) - set(get(arm, s, ck)['_solved_either']) if G[s][n] == 'C']) for s in SEEDS)
        out['sign'][f'{arm}|{ck}'] = {'grpo_only': a, 'ei_only': b, 'p': binom_two_sided(a, b), 'per_seed': per, 'C_grpo_only': aC, 'C_ei_only': bC, 'C_p': binom_two_sided(aC, bC)}
        print(f'{arm:9s} {ck}: GRPO-only {a}  EI-only {b}  p={binom_two_sided(a, b):.4f}  per seed {per} | within C: {aC} vs {bC} p={binom_two_sided(aC, bC):.3f}')

print('\n== truncation (fraction of samples cut by action/step cap; max over reference_lines strata)')
for c in out['cells']:
    m = max(c['trunc_x0'], c['trunc_x1']); ms = max(c['trunc_maxstratum_x0'], c['trunc_maxstratum_x1'])
    if ms > 0.001:
        print(f"{c['arm']:9s} s{c['seed']} {c['ck']}: overall {m:.4f}  worst stratum {ms:.4f}")

# end reads: held-out greedy, dev
print('\n== end reads (held-out greedy k1 T0; dev1108 k64)')
end = {}
for arm in ['ei'] + ['gb_' + a for a in ARMS]:
    for s in SEEDS:
        for p in ('held', 'dev'):
            f = f'{R}/eval/{arm}_s{s}_r8__{p}_x0.jsonl'
            if not os.path.exists(f): continue
            d = load(f)
            end[f'{arm}|{s}|{p}'] = (sum(1 for r in d.values() if r['n_ok']), len(d), d[next(iter(d))]['n_tried'])
for k, v in end.items(): print(k, v, f'{v[0] / v[1]:.4f}')
out['end'] = end
for c in out['cells']: c.pop('_solved_either')
json.dump(out, open(os.path.expanduser('~/review/grpo-best/review_gb/recount.json'), 'w'), indent=0, default=str)
