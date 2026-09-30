#!/usr/bin/env python3
"""Reviewer (long-pool-2), phase 1: per-model / per-stratum solve counts from the raw re-read rows (own code).

  python3 rv/rv_lp2_rates.py > rv/rates.txt
"""
import json, os, re, random, collections, statistics

R = os.path.expanduser('~/review/long-pool-2')
RR = f'{R}/artifacts/lpool2/rr'
MODELS = [('SN-cap12 T1', 'T1_SN12_s{}', 4), ('SN-cap12 frozen (Stage-1)', 'stage1_SN12_s{}', 4),
          ('K12 whole-proof T1', 'T1_K12_s{}', 2), ('SN-v2 cap-6 T1', 'T1_SNv2_s{}', 2)]


def rows(fn):
    return [json.loads(l) for l in open(fn) if l.strip()]


def nlines(p):
    return len([t for t in p.split(' ; ') if t.strip() and t.strip() != 'QED'])


def iqm(v):
    v = sorted(v); n = len(v); q = n // 4
    mid = v[q:n - q] if n >= 4 else v
    return sum(mid) / len(mid)


def boot_iqm(v, B=10000, seed=0):
    rnd = random.Random(seed)
    xs = sorted(iqm([rnd.choice(v) for _ in v]) for _ in range(B))
    return xs[int(0.025 * B)], xs[int(0.975 * B) - 1]


def wilson(k, n, z=1.96):
    if n == 0:
        return (0, 0)
    p = k / n; d = 1 + z * z / n; c = p + z * z / (2 * n); h = z * ((p * (1 - p) + z * z / (4 * n)) / n) ** 0.5
    return ((c - h) / d, (c + h) / d)


def main():
    pool = {r['name']: r for r in rows(f'{R}/data/ladder/transfer_long2.jsonl')}
    cal = {r['name']: r for r in rows(f'{R}/data/ladder/transfer_long2_calib.jsonl')}
    both = {**pool, **cal}
    # own strata: 17 = exact 17 (stage E found 17); 18 = stage F found 18; ge18 = stage E no proof, F not resolved
    def strat(r):
        if r['stageE'] == 'exact17':
            return '17'
        if r['stageE'] == 'ge18':
            return '18' if r['stageF'] == 'exact18' else '>=18 (F open)'
        return '>=17'
    def cbin(r):         # construction length after pruning (not the stage-E-tightened bound)
        c = r['construction_pruned']
        return '<=28' if c <= 28 else '29-32' if c <= 32 else '33-36' if c <= 36 else '37+'
    solved = {}
    minw = collections.defaultdict(list)
    for tag, fam, ns in MODELS:
        for s in range(ns):
            for part, P in (('new', pool), ('cal', cal)):
                fn = f'{RR}/{fam.format(s)}__{part}.jsonl'
                rs = rows(fn)
                assert len(rs) == len(P) and {r['name'] for r in rs} == set(P), fn
                for r in rs:
                    ok = bool(r['proofs'])
                    assert ok == r['solved'] and r['n_tried'] == 256, (fn, r['name'])
                    assert all(p.rstrip().endswith('QED') for p in r['proofs'])
                    solved[(fam.format(s), r['name'])] = ok
                    for p in r['proofs']:
                        minw[(tag, strat(P[r['name']]))].append(nlines(p))
    print('# solved counts (own recount from rr/*.jsonl, proofs non-empty)')
    groups = {
        'new (21)': [n for n in pool],
        'calib (70)': [n for n in cal],
        'all (91)': list(both),
    }
    for sname in ('17', '18', '>=18 (F open)'):
        for gname, P in (('new', pool), ('cal', cal), ('all', both)):
            groups[f'{gname} stratum {sname}'] = [n for n, r in P.items() if strat(r) == sname]
    for gname, P in (('new', pool), ('cal', cal), ('all', both)):
        groups[f'{gname} stratum >=18 (18 + F open)'] = [n for n, r in P.items() if r['stageE'] == 'ge18']
    for b in ('<=28', '29-32', '33-36', '37+'):
        for gname, P in (('new', pool), ('cal', cal), ('all', both)):
            groups[f'{gname} construction {b}'] = [n for n, r in P.items() if cbin(r) == b]
    for b in ('17-18', '19-20', '21-22', '23-24', '25+'):
        groups[f'all L_ub bin {b}'] = [n for n, r in both.items() if r['ub_bin'] == b]
    out = {}
    for g, names in groups.items():
        line = [f'{g:38s} n={len(names):3d}']
        for tag, fam, ns in MODELS:
            ks = [sum(solved[(fam.format(s), n)] for n in names) for s in range(ns)]
            out[(g, tag)] = ks
            line.append(f'{tag.split()[0]}{"F" if "frozen" in tag else ""}:' + '/'.join(map(str, ks)))
        print('  '.join(line))
    print()
    print('# IQM over seeds (4-seed arms), rate %, with seed-bootstrap 95% interval')
    for g in ('new (21)', 'calib (70)', 'all (91)', 'all stratum 17', 'all stratum >=18 (18 + F open)', 'new stratum 17', 'new stratum >=18 (18 + F open)',
              'cal stratum 17', 'cal stratum >=18 (18 + F open)'):
        n = len(groups[g])
        for tag, fam, ns in MODELS[:2]:
            v = [100 * k / n for k in out[(g, tag)]]
            lo, hi = boot_iqm(v)
            print(f'  {g:34s} {tag:26s} per-seed {["%.1f" % x for x in v]} IQM {iqm(v):.1f} [{lo:.1f}, {hi:.1f}]')
    print()
    print('# stratum 17 vs >=18 per seed, all 91 (difference in pp) and paired-by-theorem is impossible (different theorems);')
    n17 = len(groups['all stratum 17']); n18 = len(groups['all stratum >=18 (18 + F open)'])
    for tag, fam, ns in MODELS[:2]:
        a = out[('all stratum 17', tag)]; b = out[('all stratum >=18 (18 + F open)', tag)]
        print(f'  {tag}: ' + ', '.join(f's{s} {100*a[s]/n17:.1f} vs {100*b[s]/n18:.1f} (Δ {100*a[s]/n17-100*b[s]/n18:+.1f})' for s in range(ns)))
        pa = sum(a) / (ns * n17); pb = sum(b) / (ns * n18)
        print(f'    4-seed mean {100*pa:.1f} vs {100*pb:.1f}, Δ {100*(pa-pb):+.1f} pp; Wilson on seed-pooled: {wilson(sum(a), ns*n17)} {wilson(sum(b), ns*n18)}')
    # theorem-level bootstrap for the SN-cap12 T1 17-vs->=18 difference (4-seed mean rate), resampling theorems within strata
    rnd = random.Random(1)
    A = [sum(solved[(f'T1_SN12_s{s}', n)] for s in range(4)) / 4 for n in groups['all stratum 17']]
    Bv = [sum(solved[(f'T1_SN12_s{s}', n)] for s in range(4)) / 4 for n in groups['all stratum >=18 (18 + F open)']]
    ds = sorted(sum(rnd.choice(A) for _ in A) / len(A) - sum(rnd.choice(Bv) for _ in Bv) / len(Bv) for _ in range(20000))
    print(f'  SN-cap12 T1 4-seed-mean Δ(17 − ≥18) theorem bootstrap 95% [{100*ds[500]:.1f}, {100*ds[19499]:.1f}] pp')
    print()
    print('# written-length of accepted proofs by stratum (min / median)')
    for k, v in sorted(minw.items()):
        v.sort(); print(f'  {k[0]:26s} stratum {k[1]:14s} n_proofs {len(v):5d} min {v[0]} median {v[len(v)//2]}')
    json.dump({f'{k[0]}|{k[1]}': v for k, v in solved.items()}, open(f'{R}/rv/solved.json', 'w'))


if __name__ == '__main__':
    main()
