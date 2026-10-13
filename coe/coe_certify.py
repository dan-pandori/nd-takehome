#!/usr/bin/env python3
"""create-or-elicit: the knockout bases' certificates on the strict sigma-covered held-out members (pre-registration
"Knockout bases on the classical families"; Addendum 2; the 105-member family pool per the 2026-10-13 top-up note).

Per knockout seed: attempts and successes of its pend on each member, pooled over the 105 family members (the strict 106
minus the generated la_transfer_916), from post.sh's sample (`sig178_ko_s<S>`) plus the top-up (`sig105_topup_ko_s<S>`).
Certified at K = K_train(16) of that seed iff the one-sided 95 % Clopper-Pearson upper bound of the pooled mean p is below
0.05 / K.  Per family: the same bound and the largest K it certifies (0.05 / UB95).  la_transfer_916 reported separately.

  python3 coe/coe_certify.py --out artifacts/coe/certificates.json
"""
import argparse, json, os
from scipy.stats import beta


def ub95(c, n):
    return 1.0 if n == 0 else (float(beta.ppf(0.95, c + 1, n - c)) if c < n else 1.0)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', required=True)
    a = ap.parse_args()
    fam = json.load(open('data/coe/families.json'))
    fams = {f: d['strict_heldout'] for f, d in fam['families'].items() if d['classical']}
    allf = set(n for v in fams.values() for n in v)
    res = {}
    print('| knockout seed | K_train(16) | 105 family members: attempts / successes | UB95 vs 0.05 / K | certified | la_transfer_916: successes / attempts | per family: largest K certified |')
    print('|---|---|---|---|---|---|---|')
    for s in range(6):
        N = f'ko_s{s}'
        kf = f'artifacts/coe/budget/k_{N}.json'
        files = [f'artifacts/coe/large/sig178_{N}.json', f'artifacts/coe/large/sig105_topup_{N}.json']
        if not os.path.exists(kf) or not os.path.exists(files[0]):
            print(f'| s{s} | missing |'); continue
        K = json.load(open(kf))['K_train16']
        tot = {}
        for fn in files:
            if not os.path.exists(fn):
                continue
            for n, v in json.load(open(fn))['theorems'].items():
                t = tot.setdefault(n, [0, 0]); t[0] += v['ok']; t[1] += v['tried']
        c = sum(tot.get(n, [0, 0])[0] for n in allf); n_ = sum(tot.get(n, [0, 0])[1] for n in allf)
        u = ub95(c, n_)
        perf = {}
        for f, m in fams.items():
            cf = sum(tot.get(x, [0, 0])[0] for x in m); nf = sum(tot.get(x, [0, 0])[1] for x in m)
            uf = ub95(cf, nf)
            perf[f] = {'c': cf, 'n': nf, 'ub95': uf, 'K_certified': 0.05 / uf}
        t916 = tot.get('la_transfer_916', [0, 0])
        res[N] = {'K_train16': K, 'pool105': {'c': c, 'n': n_, 'ub95': u, 'threshold': 0.05 / K, 'certified': u < 0.05 / K},
                  'per_family': perf, 'la_transfer_916': {'c': t916[0], 'n': t916[1]}, 'topup_present': os.path.exists(files[1]),
                  'members_with_success': sorted(n for n, v in tot.items() if v[0] > 0)}
        print(f"| s{s} | {K:,.0f} | {n_:,} / {c} | {u:.2e} vs {0.05 / K:.2e} | {'yes' if u < 0.05 / K else 'no'}{'' if res[N]['topup_present'] else ' (no top-up yet)'} | "
              f"{t916[0]} / {t916[1]:,} | " + ', '.join(f"{f[:8]} {v['K_certified']:,.0f}" for f, v in perf.items()) + ' |')
    json.dump(res, open(a.out, 'w'), indent=1)


if __name__ == '__main__':
    main()
