#!/usr/bin/env python3
"""Reviewer: J2 (stage A, A', B, doubled-cap t, calibration), J9 certification chunks, J10 long pool.
Counts successes / attempts per theorem from the raw rows; truncation (action truncated / step cap) per stratum."""
import json, os, sys, glob, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rv_load as L
CD = L.CD
TR = ('lean_seq parse: env: action truncated', 'lean_seq parse: env: step cap')
S = json.load(open(f'{L.RV}/review_cd/out_sets.json'))
EX = json.load(open(f'{CD}/j1/sets.json'))


def reasons_count(r):
    rs = r.get('reasons') or []
    return collections.Counter(rs) if isinstance(rs, list) else collections.Counter(rs)


def load_stage(s, pref):
    d = collections.defaultdict(lambda: [0, 0, 0, set(), 0])  # ok, tried, truncated, proofs, reasons_total
    files = sorted(glob.glob(f'{CD}/j2/s{s}_{pref}*.jsonl'))
    for p in files:
        for r in L.rows(p):
            c = d[r['name']]; c[0] += r['n_ok']; c[1] += r['n_tried']
            rc = reasons_count(r); c[2] += sum(rc[t] for t in TR); c[3].update(r.get('proofs') or []); c[4] += sum(rc.values())
    return d, files


res = {}
for s in (0, 1, 2):
    A, fa = load_stage(s, 'c0')
    CAL, _ = load_stage(s, 'cal')
    D, _ = load_stage(s, 'd')
    B, _ = load_stage(s, 'b')
    T, _ = load_stage(s, 't')
    J2x, J2m = EX[str(s)]['J2'], S['J2'][str(s)]
    Hm = S['H'][str(s)]
    def share(names, st):
        hit = [n for n in names if st[n][0] > 0]
        return len(hit), len(names)
    # consistency: every theorem got the advertised k
    kA = collections.Counter(A[n][1] for n in J2x); kD = collections.Counter(D[n][1] for n in D); kB = collections.Counter(B[n][1] for n in B)
    print(f's{s}: stage A k {dict(kA)}; A\' k {dict(kD)}; B k {dict(kB)}; cal k {dict(collections.Counter(v[1] for v in CAL.values()))}')
    h, n = share(J2x, A)
    print(f'  Q2 stage A (exec J2 set, {n}): >=1 base success {h}/{n} = {h / n:.3f}', end='')
    hm = [t for t in J2m if (A[t][0] if t in A else D[t][0]) > 0]
    print(f';  my J2 set ({len(J2m)}; extra theorems were sampled in A\'): {len(hm)}/{len(J2m)} = {len(hm) / len(J2m):.3f}')
    Ap = [t for t in Hm if t not in J2x]
    h2 = [t for t in Ap if D[t][0] > 0]
    Ap_m = [t for t in Hm if t not in J2m]
    print(f'  A\' (exec: H - J2, {len(Ap)}): >=1 base success {len(h2)}/{len(Ap)}  {sorted(h2)};  on my H-J2 ({len(Ap_m)}): {sum(D[t][0] > 0 for t in Ap_m)}')
    zA = [t for t in J2x if A[t][0] == 0]
    inB = [t for t in zA if t in B]
    stay0 = [t for t in zA if B[t][0] == 0]
    print(f'  B: stage-A zeros {len(zA)}; sampled in B {len(inB)}; still 0 / {16384 + 49152} after B: {len(stay0)} ({len(stay0) / len(zA):.2f}); B successes on {sorted(t for t in zA if B[t][0] > 0)}')
    # truncation per stratum (attempt-weighted), per theorem max
    for lab, st, names in (('stage A (J2)', A, J2x), ('calibration', CAL, list(CAL)), ("A'", D, list(D)), ('B', B, list(B))):
        tt = sum(st[t][2] for t in names); nn = sum(st[t][1] for t in names)
        mx = max((st[t][2] / st[t][1], t) for t in names)
        over = sum(st[t][2] / st[t][1] > 0.001 for t in names)
        print(f'  truncation {lab:13s}: {tt}/{nn} = {100 * tt / nn:.3f} %  theorems > 0.1 %: {over}/{len(names)}  max {100 * mx[0]:.2f} % ({mx[1]})')
    # doubled-cap re-reads
    print(f'  t (doubled caps, 16,384): theorems {len(T)}: ' + ', '.join(f'{t} {T[t][0]}/{T[t][1]} trunc {100 * T[t][2] / T[t][1]:.3f}%' for t in T))
    zA_tr = [t for t in zA if A[t][2] / A[t][1] > 0.001]
    print(f'  stage-A zeros with > 0.1 % cut off: {len(zA_tr)} {sorted(zA_tr)}  == t set: {set(zA_tr) == set(T)}')
    res[s] = dict(A={t: A[t][:3] for t in A}, D={t: D[t][:3] for t in D}, B={t: B[t][:3] for t in B}, T={t: T[t][:3] for t in T},
                  CAL={t: CAL[t][:3] for t in CAL})
json.dump(res, open(f'{L.RV}/review_cd/out_j2.json', 'w'))
