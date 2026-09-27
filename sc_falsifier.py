#!/usr/bin/env python3
"""The pre-registered falsifier, counted from artifacts/sc/summary.json.

FALSIFIER (support expansion): >= 20 forward-crux theorems with 0 base successes in >= 40,000 attempts at
BOTH temperatures while the EI model solves each at p-hat_EI >= 0.01.

Forward crux = EI solved it in stage 1 and the base did not.  Reported at the pre-registered k = 4,000 and at
the k = 10,000 stage 1 actually ran (addendum 1); `first_hit` makes the 4,000 prefix exact.
"""
import json, collections, sys

cells = json.load(open('artifacts/sc/summary.json'))
by = {(c['name'], c['model'], c['temperature'], c['seed']): c for c in cells}
names = sorted({c['name'] for c in cells})
L = {c['name']: c['L_true'] for c in cells}


def s1_hit(c, k):
    fh = c['stages'].get('s1', {}).get('first_hit') if c else None
    return fh is not None and fh <= k


for KCRUX in (4000, 10000):
    base08 = {n: by.get((n, 'base', 0.8, 0)) for n in names}
    base10 = {n: by.get((n, 'base', 1.0, 0)) for n in names}
    ei08 = {n: by.get((n, 'ei', 0.8, 0)) for n in names}
    fwd = [n for n in names if ei08.get(n) and base08.get(n) and s1_hit(ei08[n], KCRUX) and not s1_hit(base08[n], KCRUX)]
    phi = [n for n in fwd if ei08[n]['p_hat'] and ei08[n]['p_hat'] >= 0.01]
    surv, partial = [], []
    for n in phi:
        b8, b10 = base08[n], base10.get(n)
        n8, c8 = b8['n'], b8['c']
        n10, c10 = (b10['n'], b10['c']) if b10 else (0, 0)
        if c8 == 0 and c10 == 0 and n8 >= 40000 and n10 >= 40000:
            surv.append((n, n8, n10, ei08[n]['p_hat']))
        elif c8 == 0 and c10 == 0:
            partial.append((n, n8, n10))
    print(f'=== crux at k={KCRUX} ===')
    print(f'  forward crux: {len(fwd)}   of which p_EI >= 0.01 (falsifier-eligible): {len(phi)}')
    print(f'  FALSIFIER COUNT (0 base successes, >= 40,000 attempts at BOTH T, p_EI >= 0.01): {len(surv)}'
          f'   [fires at >= 20: {"YES" if len(surv) >= 20 else "no"}]')
    print(f'  still 0/0 but under 40,000 at one temperature (arms still running): {len(partial)}')
    if surv:
        mn8 = min(x[1] for x in surv); mn10 = min(x[2] for x in surv)
        print(f'  survivors: min attempts T0.8 {mn8:,}  T1.0 {mn10:,};  p_EI range '
              f'{min(x[3] for x in surv):.3f}-{max(x[3] for x in surv):.3f}')
        print('  by L_true:', dict(sorted(collections.Counter(L[x[0]] for x in surv).items())))
    if KCRUX == 10000:
        open('data/sc/falsifier_survivors.txt', 'w').write('\n'.join(x[0] for x in surv) + '\n')
