#!/usr/bin/env python3
"""Reviewer recount of the search-expert read-out (independent of executor analysis code)."""
import json, glob, os, random, statistics as S, collections, math
R = os.path.expanduser('~/review/search-expert'); A = f'{R}/artifacts/sx/rr'
def load(f): return [json.loads(l) for l in open(f) if l.strip()]
l2 = {r['name']: r for r in load(f'{R}/data/ladder/transfer_long2_91.jsonl')}
rr = {r['name']: r for r in load(f'{R}/data/ladder/rr600_13to16.jsonl')}
def lt(r):
    return r['L_true_lb'] if 'L_true_lb' in r else r['L_true']
print('pool sizes', len(l2), len(rr), 'l2 L:', collections.Counter(lt(r) for r in l2.values()),
      'rr L:', collections.Counter(lt(r) for r in rr.values()))
Qnames = set(l2) | {n for n, r in rr.items() if lt(r) in (15, 16)}
print('Q size', len(Qnames))
arms = collections.defaultdict(dict)   # arm -> seed -> {name: row}
issues = []
for f in sorted(glob.glob(f'{A}/*__l2.jsonl')) + sorted(glob.glob(f'{A}/*__rr1316.jsonl')):
    tag = os.path.basename(f).split('__')[0]; arm, s = tag.rsplit('_s', 1)
    for r in load(f):
        # own consistency checks: solved <-> proofs nonempty; n_ok + fails == n_tried
        nf = sum(r['reasons'].values())
        if bool(r['proofs']) != r['solved'] or r['n_ok'] + nf != r['n_tried'] or r['n_tried'] != 256:
            issues.append((tag, r['name'], r['n_ok'], nf, r['n_tried']))
        arms[arm].setdefault(int(s), {})[r['name']] = r
print('consistency issues', len(issues), issues[:5])
def solved(arm, s, names):
    d = arms[arm][s]; assert names <= set(d), (arm, s, len(names - set(d)))
    return {n for n in names if d[n]['solved']}
strata = {'Q': Qnames, 'l2_17': {n for n, r in l2.items() if lt(r) == 17}, 'l2_ge18': {n for n, r in l2.items() if lt(r) >= 18},
          'rr13_14': {n for n, r in rr.items() if lt(r) in (13, 14)}, 'rr15_16': {n for n, r in rr.items() if lt(r) in (15, 16)},
          'l2_91': set(l2)}
print({k: len(v) for k, v in strata.items()})
tab = {}
for arm in sorted(arms):
    for s in sorted(arms[arm]):
        tab[(arm, s)] = {k: len(solved(arm, s, v)) for k, v in strata.items()}
        print(arm, s, tab[(arm, s)])
def iqm(xs):
    xs = sorted(xs); n = len(xs); lo = n // 4; hi = n - lo  # trimmed 25% each side (discrete)
    return S.mean(xs[lo:hi]) if n >= 4 else S.mean(xs)
def boot(xs, f=iqm, B=20000, seed=0):
    rnd = random.Random(seed); v = sorted(f([rnd.choice(xs) for _ in xs]) for _ in range(B))
    return v[int(.025 * B)], v[int(.975 * B)]
out = {'tab': {f'{a}_s{s}': v for (a, s), v in tab.items()}}
for k in strata:
    for arm in sorted(arms):
        xs = [tab[(arm, s)][k] for s in sorted(arms[arm])]
        print(f'{k:8s} {arm:3s} per-seed {xs} mean {S.mean(xs):.2f} IQM {iqm(xs):.2f} CI {boot(xs)}')
# paired B - A
seeds = sorted(set(arms['A']) & set(arms['B']))
for k in strata:
    d = [tab[('B', s)][k] - tab[('A', s)][k] for s in seeds]
    sd = S.stdev(d)
    t = S.mean(d) / (sd / math.sqrt(len(d))) if sd else float('nan')
    print(f'B-A {k}: {d} mean {S.mean(d):.2f} sd {sd:.2f} t {t:.2f} IQM {iqm(d):.2f} CI {boot(d)}')
    out[f'BminusA_{k}'] = d
# per-theorem discordance B vs A on Q
for s in seeds:
    a = solved('A', s, Qnames); b = solved('B', s, Qnames)
    print(f'seed {s}: Q A {len(a)} B {len(b)} B-only {len(b-a)} A-only {len(a-b)}')
# same-checkpoint spread A vs A2, and C vs A2
for k in ('Q',):
    diffs = []
    for s in sorted(arms['A2']):
        a = solved('A', s, strata[k]); a2 = solved('A2', s, strata[k])
        diffs.append(len(a) - len(a2))
        print(f'A vs A2 seed {s}: A {len(a)} A2 {len(a2)} flips A-only {len(a-a2)} A2-only {len(a2-a)}')
    s_ = math.sqrt(S.mean([(x / math.sqrt(2)) ** 2 for x in diffs]))
    mdd = (2.571 + 0.920) / math.sqrt(6) * math.sqrt(2) * s_
    print(f's (RMS (A-A2)/sqrt2) = {s_:.2f}; MDD(6 pairs) = {mdd:.2f}')
    dBA = out['BminusA_Q']; sdd = S.stdev(dBA)
    print(f'MDD from between-seed sd of B-A ({sdd:.2f}): {(2.571+0.920)/math.sqrt(6)*sdd:.2f}')
    for s in sorted(arms['C']):
        c = solved('C', s, strata[k]); a2 = solved('A2', s, strata[k]); a = solved('A', s, strata[k])
        print(f'C seed {s}: C {len(c)} A2 {len(a2)} A {len(a)} C-A2 {len(c)-len(a2)}')
json.dump(out, open(f'{R}/rv/recount_rr.json', 'w'), indent=1)
