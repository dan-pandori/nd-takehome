#!/usr/bin/env python3
"""Reviewer M3 analysis from rv/m3/*.json (own per-file summaries).  Ladder -> (family, arm, role, seed) mapping taken
from the executor's per_round.tsv columns 2-6 (metadata only); every count recomputed here."""
import json, glob, os, collections, itertools, csv
R = '/home/dan/review/lit-measures'
M = {}
for row in csv.DictReader(open(f'{R}/artifacts/lit-measures/m3/per_round.tsv'), delimiter='\t'):
    M[row['ladder']] = (row['family'], row['arm'], row['role'], int(row['seed']))
EX = collections.defaultdict(dict)
for row in csv.DictReader(open(f'{R}/artifacts/lit-measures/m3/per_round.tsv'), delimiter='\t'):
    EX[(row['pool'], row['ladder'])][int(row['round'])] = (int(row['n_new']), row['new_d3p'])
data = {}
LASTR = {}
mism = 0; checked = 0
for f in glob.glob(f'{R}/rv/m3/*.json'):
    d = json.load(open(f)); src = d['src']
    base = os.path.basename(src)           # /tmp/rvm3/<path with _>
    for lad in M:
        key = lad.replace('/', '_') + '_'
        if base.startswith(key) and (base[len(key):].startswith('found_')):
            pool = 'found_transfer' if 'found_transfer' in base[len(key):] else 'found'
            pr = {int(k): v for k, v in d['per_round'].items()}
            data[(pool, lad)] = pr
            LASTR[(pool, lad)] = max([int(k) for k in d.get('raw_rows', {})] + list(pr) + [0])
            for r, (n, s) in EX.get((pool, lad), {}).items():
                checked += 1
                mine = pr.get(r, {'rows': 0, 'd': [0, 0, 0, 0]})
                if mine['rows'] != n or (n and abs(mine['d'][3] / n - float(s)) > 6e-5):
                    mism += 1
                    if mism <= 5: print('MISMATCH', pool, lad, r, n, s, mine['rows'], mine['d'])
rawchk = [0, 0]
for f in glob.glob(f'{R}/rv/m3/round3-run4b_*.json'):
    d = json.load(open(f)); b = os.path.basename(d['src'])
    for (pool, lad), v in EX.items():
        k = lad.replace('/', '_') + '_'
        if b.startswith(k) and ((pool == 'found_transfer') == ('found_transfer' in b)):
            for r, (n, s_) in v.items():
                rawchk[0] += 1; rawchk[1] += d.get('raw_rows', {}).get(str(r), 0) != n
print(f'round3-run4b: executor n_new vs RAW rows (no start-index dedup): {rawchk[0]} cells, {rawchk[1]} differ')
print(f'per-round rows vs executor per_round.tsv: {checked} (ladder, round) cells checked, {mism} differ')
LAST = 8
def cum_share(pr, r):
    n = sum(pr.get(k, {'rows': 0})['rows'] for k in range(1, r + 1)); d = sum(pr.get(k, {'d': [0, 0, 0, 0]})['d'][3] for k in range(1, r + 1))
    return d / n if n else None
def range_share(pr, a, b):
    n = sum(pr.get(k, {'rows': 0})['rows'] for k in range(a, b + 1)); d = sum(pr.get(k, {'d': [0, 0, 0, 0]})['d'][3] for k in range(a, b + 1))
    return d / n if n else None
def groups(pool, role):
    g = collections.defaultdict(dict)
    for (p, lad), pr in data.items():
        if p != pool or lad not in M: continue
        fam, arm, rl, seed = M[lad]
        if rl != role: continue
        if LASTR[(p, lad)] < LAST: continue
        g[(fam, arm)][seed] = pr
    return {k: v for k, v in g.items() if len(v) >= 2}
def agree(pairs):
    s = 0; n = 0; strict = 0
    for x, y in pairs:
        if x is None or y is None: continue
        if y == 0: continue          # final ordering tied (e.g. both 0): pair undefined, dropped
        n += 1
        if x == 0: s += 0.5; continue
        s += (x > 0) == (y > 0); strict += (x > 0) == (y > 0)
    return s, strict, n
res = {}
for pool in ('found', 'found_transfer'):
    for role in ('headline', 'frozen', 'extra'):
        G = groups(pool, role)
        if not G: continue
        out = []
        for r in range(1, LAST + 1):
            P_cum, P_new, P_dis = [], [], []
            for k, seeds in G.items():
                for a, b in itertools.combinations(sorted(seeds), 2):
                    A, B = seeds[a], seeds[b]
                    fin = cum_share(A, LAST) - cum_share(B, LAST)
                    ca, cb = cum_share(A, r), cum_share(B, r)
                    P_cum.append((None if ca is None or cb is None else ca - cb, fin))
                    na, nb = range_share(A, r, r), range_share(B, r, r)
                    P_new.append((None if na is None or nb is None else na - nb, fin))
                    if r < LAST:   # disjoint: rounds 1..r vs rounds r+1..8
                        la, lb = range_share(A, r + 1, LAST), range_share(B, r + 1, LAST)
                        P_dis.append((None if ca is None or cb is None else ca - cb, None if la is None or lb is None else la - lb))
            out.append((r, agree(P_cum), agree(P_new), agree(P_dis) if P_dis else None))
        res[(pool, role)] = (G, out)
        print(f'\n[{pool}] {role}: {len(G)} arms, {sum(len(list(itertools.combinations(v, 2))) for v in G.values())} within-arm pairs')
        for r, c, nw, ds in out:
            f = lambda t: f'{t[0]:.1f}/{t[2]} ({t[0]/t[2]:.2f}; strict {t[1]})' if t and t[2] else '-'
            print(f'  r{r}: cumulative {f(c)} | new-that-round {f(nw)} | disjoint rounds1..r vs r+1..8 {f(ds)}')
# per-arm final shares and round-2 cumulative / late shares, headline found
G, _ = res[('found', 'headline')]
print('\nheadline found, per arm: seed: cum share r2 / cum r8 / new r3-8 share')
for k in sorted(G):
    print(' ', k, '  '.join(f"s{s}: {cum_share(p,2):.3f}/{cum_share(p,8):.3f}/{range_share(p,3,8):.3f}" for s, p in sorted(G[k].items())))
# E3.2 monotone
mono = 0; tot = 0
for (fam, arm), seeds in G.items():
    for s, p in seeds.items():
        v = [range_share(p, r, r) for r in range(1, LAST + 1)]
        v = [x for x in v if x is not None]
        tot += 1
        inc = all(v[i] <= v[i + 1] for i in range(len(v) - 1)); dec = all(v[i] >= v[i + 1] for i in range(len(v) - 1))
        mono += inc or dec
print(f'\nE3.2 strictly monotone new-proof depth>=3 share across 8 rounds: {mono}/{tot} headline ladders (found pool)')
print('\nbimodal arms (round3-run4b r-arms), cumulative depth>=3 share by round (start-index-deduplicated) and distinct proofs found:')
for k in [('round3-run4b', 'ei_depth3_25Mr_mix'), ('round3-run4b', 'ei_depth3_85Mr_mix')]:
    for s, p in sorted(G[k].items()):
        print(' ', k[1], f's{s}', ' '.join(f"r{r}:{cum_share(p, r):.3f}" for r in range(1, 9)), '| n', sum(v['rows'] for v in p.values()))
inc_n = dec_n = 0
for (fam, arm), seeds in G.items():
    for s, p in seeds.items():
        v = [x for x in (range_share(p, r, r) for r in range(1, LAST + 1)) if x is not None]
        inc_n += all(v[i] <= v[i + 1] for i in range(len(v) - 1)); dec_n += all(v[i] >= v[i + 1] for i in range(len(v) - 1))
print(f'E3.2 split: non-decreasing {inc_n}, non-increasing {dec_n} (a constant-0 ladder counts in both)')
