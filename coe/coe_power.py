#!/usr/bin/env python3
"""create-or-elicit: power of the arm comparison (pre-registration), exact.

Per-seed acquisition of a family (held-out rate >= 0.5 at r16) is Bernoulli(q_full) in the full arm and
Bernoulli(q_ko) in the knockout arm. Test: one-sided Fisher exact (full > knockout) at alpha 0.05, and
Boschloo's test (more powerful for small n; scipy). Also P(knockout acquires on >= 2 seeds) = the "created" rule.

  python3 coe/coe_power.py [--n_full 6] [--n_ko 6]
"""
import argparse, itertools
from math import comb
from scipy.stats import fisher_exact, boschloo_exact


def binom(n, k, q):
    return comb(n, k) * q ** k * (1 - q) ** (n - k)


def reject_table(nf, nk, alpha, test):
    rej = {}
    for a, b in itertools.product(range(nf + 1), range(nk + 1)):
        tab = [[a, nf - a], [b, nk - b]]
        if test == 'fisher':
            p = fisher_exact(tab, alternative='greater')[1]
        else:
            p = boschloo_exact(tab, alternative='greater').pvalue
        rej[(a, b)] = p <= alpha
    return rej


def power(nf, nk, qf, qk, rej):
    return sum(binom(nf, a, qf) * binom(nk, b, qk) for (a, b), r in rej.items() if r)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--n_full', type=int, default=6)
    ap.add_argument('--n_ko', type=int, default=6)
    ap.add_argument('--alpha', type=float, default=0.05)
    a = ap.parse_args()
    grid_f = [1.0, 0.9, 0.67, 0.5, 0.33]
    grid_k = [0.0, 0.1, 0.2, 0.33]
    for test in ('fisher', 'boschloo'):
        rej = reject_table(a.n_full, a.n_ko, a.alpha, test)
        print(f'## {test}, one-sided alpha {a.alpha}, n_full {a.n_full}, n_ko {a.n_ko}')
        print('smallest rejecting tables (full acquired, knockout acquired):',
              sorted([k for k, v in rej.items() if v], key=lambda x: (x[1], x[0]))[:8])
        print('| q_full \\ q_ko | ' + ' | '.join(f'{q:.2f}' for q in grid_k) + ' |')
        print('|---|' + '---|' * len(grid_k))
        for qf in grid_f:
            print(f'| {qf:.2f} | ' + ' | '.join(f'{power(a.n_full, a.n_ko, qf, qk, rej):.2f}' for qk in grid_k) + ' |')
        print()
    print('P(knockout acquires on >= 2 of', a.n_ko, 'seeds) ["created" rule]:')
    for qk in (0.05, 0.1, 0.2, 0.33, 0.5):
        p2 = 1 - binom(a.n_ko, 0, qk) - binom(a.n_ko, 1, qk)
        print(f'  q_ko {qk:.2f}: {p2:.2f}')


if __name__ == '__main__':
    main()
