#!/usr/bin/env python3
"""long-pool-2 read-out tables: solved theorems per stratum / upper-bound bin, per model, on the new pool, the calibration
file and both together.  Counts come from the per-theorem re-read rows (`solved`), keyed by name.

  python3 lpool2_analysis.py --pool data/ladder/transfer_long2.jsonl --calib data/ladder/transfer_long2_calib.jsonl \
      --rows artifacts/lpool2/rr --calib_rows artifacts/lpool2/calib_rows --out artifacts/lpool2/tables.md

Strata (`stratum`): 17 = exact 17 (stage E proof) / 18 = exact 18 (stage F proof) / >=19 = stage F finished without a proof / >=18 = stage E finished without a proof, stage F not run or cut.  --calib_rows same = the calibration rows are <stem>__cal.jsonl in --rows.  Bins: construction length (the brief's upper bound; `constr`) <=28 / 29-32 / 33-36 / 37+, and the best upper bound L_ub (stage E/F proof if found, else construction) in the brief's
17-18 / 19-20 / 21-22 / 23-24 / 25+ and quartile-style <=28 / 29-32 / 33-36 / 37+.  L*_ub = the largest bin lower edge e
such that >= 5 theorems with L_ub >= e are solved (a statement about the upper bound only).
IQM + stratified-bootstrap 95 % CI over seeds for 4-seed arms (Agarwal et al. 2021; seeds resampled, 10,000 draws).
"""
import argparse, json, os, glob, random, collections, statistics

MODELS = [('SN-cap12 T1', 'T1_SN12_s{}', 4), ('SN-cap12 frozen', 'stage1_SN12_s{}', 4),
          ('K12 whole-proof T1', 'T1_K12_s{}', 2), ('SN-v2 cap-6 T1', 'T1_SNv2_s{}', 2)]
STRATA = ('17', '18', '>=19', '>=18')   # exact 17 / exact 18 / lower bound 19 / lower bound 18 (stage F not run or cut)
UB = ('17-18', '19-20', '21-22', '23-24', '25+')
Q = ('<=28', '29-32', '33-36', '37+')
QEDGE = {'<=28': 17, '29-32': 29, '33-36': 33, '37+': 37}


def iqm(xs):
    xs = sorted(xs); n = len(xs); k = n // 4
    mid = xs[k:n - k] if n >= 4 else xs
    return statistics.mean(mid)


def boot(xs, draws=10000, seed=0):
    rng = random.Random(seed); v = sorted(iqm([rng.choice(xs) for _ in xs]) for _ in range(draws))
    return v[int(0.025 * draws)], v[int(0.975 * draws) - 1]


def load_rows(d, stem, tag):
    fn = os.path.join(d, f'{stem}__{tag}.jsonl')
    if not os.path.exists(fn):
        return None
    return {r['name']: bool(r['solved']) for r in map(json.loads, open(fn))}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--pool', required=True); ap.add_argument('--calib', required=True)
    ap.add_argument('--rows', required=True); ap.add_argument('--calib_rows', required=True)
    ap.add_argument('--out', required=True); ap.add_argument('--json_out')
    a = ap.parse_args()
    pool = [json.loads(l) for l in open(a.pool)]; calib = [json.loads(l) for l in open(a.calib)]
    for r in pool + calib:   # construction length (the brief's upper bound) in quartile-style bins
        c = r['construction_pruned']; r['ub_qbin'] = '<=28' if c <= 28 else '29-32' if c <= 32 else '33-36' if c <= 36 else '37+'
    sets = {'new': pool, 'calib': calib, 'all': pool + calib}
    L = [f'# long-pool-2 tables (`lpool2_analysis.py`)', '',
         f'Pool {len(pool)} + calibration {len(calib)}. Solved = ≥ 1 Lean-accepted sample of 256 (T 0.8, seed 0).', '']
    for nm, rs in sets.items():
        c = collections.Counter(r['stratum'] for r in rs); u = collections.Counter(r['ub_bin'] for r in rs)
        q = collections.Counter(r['ub_qbin'] for r in rs)
        L.append(f'- **{nm}** n {len(rs)}: strata {dict(c)}; brief bins {[u[b] for b in UB]} ({"/".join(UB)}); '
                 f'quartile bins {[q[b] for b in Q]} ({"/".join(Q)})')
    L.append('')
    res, J = {}, {}
    for label, stem, ns in MODELS:
        for s in range(ns):
            st = stem.format(s)
            new = load_rows(a.rows, st, 'new'); cal = load_rows(a.rows, st, 'cal') if a.calib_rows == 'same' else load_rows(a.calib_rows, st, 'ge17')
            if new is None and cal is None:
                continue
            solved = {**(cal or {}), **(new or {})}
            res[(label, s)] = solved
    for nm, rs in sets.items():
        L += [f'## {nm} (n {len(rs)})', '',
              '| model | seed | solved | ' + ' | '.join(f'L {x}' for x in STRATA) + ' | ' + ' | '.join(f'constr {b}' for b in Q)
              + ' | ' + ' | '.join(f'ub {b}' for b in UB) + ' | L*_constr |',
              '|---|---|---|' + '---|' * (len(STRATA) + len(Q) + len(UB) + 1)]
        nS = collections.Counter(r['stratum'] for r in rs); nQ = collections.Counter(r['ub_qbin'] for r in rs)
        nU = collections.Counter(r['ub_bin'] for r in rs)
        L.append('| (n) | | ' + str(len(rs)) + ' | ' + ' | '.join(str(nS[x]) for x in STRATA) + ' | '
                 + ' | '.join(str(nQ[b]) for b in Q) + ' | ' + ' | '.join(str(nU[b]) for b in UB) + ' | |')
        for (label, s), solved in res.items():
            have = [r for r in rs if r['name'] in solved]
            if len(have) < len(rs):
                continue
            ok = [r for r in rs if solved[r['name']]]
            cS = collections.Counter(r['stratum'] for r in ok); cQ = collections.Counter(r['ub_qbin'] for r in ok)
            cU = collections.Counter(r['ub_bin'] for r in ok)
            lstar = max([e for b, e in QEDGE.items() if sum(1 for r in ok if r['construction_pruned'] >= e) >= 5], default=None)
            pct = lambda k, n: f'{k} ({100 * k / n:.0f} %)' if n else '—'
            L.append(f'| {label} | s{s} | {pct(len(ok), len(rs))} | ' + ' | '.join(pct(cS[x], nS[x]) for x in STRATA) + ' | '
                     + ' | '.join(pct(cQ[b], nQ[b]) for b in Q) + ' | ' + ' | '.join(pct(cU[b], nU[b]) for b in UB)
                     + f' | {"≥ " + str(lstar) if lstar else "< 17"} |')
            res_key = f'{nm}|{label}|{s}'
            J[res_key] = {'solved': len(ok), 'n': len(rs), 'stratum': {x: [cS[x], nS[x]] for x in STRATA},
                                                    'qbin': {b: [cQ[b], nQ[b]] for b in Q}, 'ubbin': {b: [cU[b], nU[b]] for b in UB},
                                                    'Lstar_ub': lstar}
        L.append('')
        # IQM over seeds, SN-cap12 T1 / frozen
        for label in ('SN-cap12 T1', 'SN-cap12 frozen'):
            for key, getter in [('solved', lambda d: d['solved'] / d['n'])] + \
                    [(f'L {x}', (lambda x: lambda d: d['stratum'][x][0] / d['stratum'][x][1] if d['stratum'][x][1] else None)(x)) for x in STRATA]:
                xs = [getter(J[f'{nm}|{label}|{s}']) for s in range(4) if f'{nm}|{label}|{s}' in J]
                xs = [x for x in xs if x is not None]
                if len(xs) == 4:
                    lo, hi = boot(xs)
                    L.append(f'- {label}, {key}: per seed {", ".join(f"{100*x:.0f}" for x in xs)} %; IQM {100*iqm(xs):.1f} % [{100*lo:.1f}, {100*hi:.1f}]')
        L.append('')
    open(a.out, 'w').write('\n'.join(L) + '\n')
    if a.json_out:
        json.dump(J, open(a.json_out, 'w'), indent=1)
    print('\n'.join(L))


if __name__ == '__main__':
    main()
