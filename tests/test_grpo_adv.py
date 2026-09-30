#!/usr/bin/env python3
"""Unit tests for the GRPO advantage variants (run `grpo-state`; `python3 tests/test_grpo_adv.py`).  Pure Python.

Hand-made groups, each checked against a value worked out by hand or by brute force:
1. default: R - mean; all-fail and all-succeed groups give zeros.
2. unlikely: the most likely correct rollout gets the smallest advantage, the least likely the largest; the hand-worked
   G = 4 group; all-succeed stays zero despite the rank shaping; beta_rank = 0 gives default.
3. passk: equals the brute-force mean over k-subsets containing i of (max R - Rbar); sums to zero; k = 1 is default;
   zero when every k-subset already contains a success (c > n - k) and on all-fail groups.
4. distinct: new proofs earn the bonus split over copies; an all-correct group with one new proof is not zero; with no
   new proofs it is default.
5. std=True: unit population std for default; Chen et al.'s sigma for passk.
"""
import itertools, math, os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from grpo_adv import group_advantages as ga

FAIL = []


def ck(cond, msg):
    print(('  ok   ' if cond else '  FAIL ') + msg)
    if not cond:
        FAIL.append(msg)


def close(a, b, tol=1e-9):
    return len(a) == len(b) and all(abs(x - y) < tol for x, y in zip(a, b))


def main():
    print('1. default')
    ck(close(ga('default', [1, 0, 0, 1]), [0.5, -0.5, -0.5, 0.5]), 'R - mean on [1,0,0,1]')
    ck(close(ga('default', [1, 0, 0, 0, 0, 0, 0, 0]), [7 / 8] + [-1 / 8] * 7), 'one success in 8')
    ck(close(ga('default', [0] * 8), [0.0] * 8) and close(ga('default', [1] * 8), [0.0] * 8), 'all-fail / all-succeed -> 0')

    print('2. unlikely (He et al. §4.1, beta_rank 0.25)')
    R = [1, 1, 0, 1]; lp = [-2.0, -9.0, -1.0, -5.0]     # ranks by likelihood: i2 (0), i0 (1), i3 (2), i1 (3)
    r = [1 - 0.25 * (4 - 1) / 4, 1 - 0.25 * (4 - 3) / 4, 0.0, 1 - 0.25 * (4 - 2) / 4]   # 0.8125, 0.9375, 0, 0.875
    mu = sum(r) / 4
    a = ga('unlikely', R, logp=lp)
    ck(close(a, [x - mu for x in r]), f'hand-worked G=4 group: {[round(x, 4) for x in a]}')
    ck(a[1] > a[3] > a[0] > 0 > a[2], 'least likely correct > ... > most likely correct > failure')
    ck(close(ga('unlikely', [1, 1, 1, 1], logp=lp), [0.0] * 4), 'all-succeed stays zero (unperturbed advantage is zero)')
    ck(close(ga('unlikely', R, logp=lp, beta_rank=0.0), ga('default', R)), 'beta_rank 0 == default')
    ck(abs(sum(a)) < 1e-12, 'sums to zero')

    print('3. passk (Chen et al. §2.4)')
    def brute(R, k):
        n = len(R); subs = list(itertools.combinations(range(n), k))
        rbar = sum(max(R[j] for j in s) for s in subs) / len(subs)
        return [sum(max(R[j] for j in s) - rbar for s in subs if i in s) / sum(1 for s in subs if i in s) for i in range(n)]
    ok = True
    for n in (4, 8):
        for k in range(1, n + 1):
            for c in range(0, n + 1):
                R = [1] * c + [0] * (n - c)
                a = ga('passk', R, k=k)
                ok &= close(a, [0.0 if abs(x) < 1e-12 else x for x in brute(R, k)]) and abs(sum(a)) < 1e-9
    ck(ok, 'equals brute force over k-subsets and sums to zero, every (n in {4,8}, k, c)')
    ck(all(close(ga('passk', R, k=1), ga('default', R)) for R in ([1, 0, 0, 0, 1, 0, 0, 0], [0, 1, 1, 1], [1, 0])), 'k = 1 == default')
    ck(close(ga('passk', [1, 1, 1, 1, 1, 0, 0, 0], k=4), [0.0] * 8), 'c = 5 > n - k = 4: every 4-subset succeeds -> 0')
    a = ga('passk', [1, 0, 0, 0, 0, 0, 0, 0], k=4)
    ck(abs(a[0] - 0.5) < 1e-12 and abs(a[1] - (0.5 - 20 / 35)) < 1e-12,
       f'hand-worked c=1, n=8, k=4: Rbar = 1/2, A_pos = 1/2, A_neg = 1/2 - C(6,3)/C(7,3) = -1/14 ({a[1]:.4f})')
    ck(ga('passk', [1, 1, 1, 0, 0, 0, 0, 0], k=4)[0] < ga('default', [1, 1, 1, 0, 0, 0, 0, 0])[0],
       'relative to default, passk moves credit toward hard groups (c = 3 of 8: smaller positive advantage)')

    print('4. distinct-proof bonus')
    a = ga('distinct', [1, 1, 0, 0], novel_keys=['p', None, None, None], bonus=0.5)
    ck(close(a, [1.5 - 2.5 / 4, 1 - 2.5 / 4, -2.5 / 4, -2.5 / 4]), 'one new proof earns +0.5')
    a = ga('distinct', [1, 1, 1, 0], novel_keys=['p', 'p', None, None], bonus=0.5)
    ck(close(a, [1.25 - 3.5 / 4, 1.25 - 3.5 / 4, 1 - 3.5 / 4, -3.5 / 4]), 'two copies of one new proof share the bonus')
    a = ga('distinct', [1, 1, 1, 1], novel_keys=[None, 'q', None, None], bonus=0.5)
    ck(a[1] > 0 and all(x < 0 for i, x in enumerate(a) if i != 1), 'all-correct group with one new proof is not zero')
    ck(close(ga('distinct', [1, 0, 1, 0], novel_keys=[None] * 4), ga('default', [1, 0, 1, 0])), 'no new proofs == default')

    print('5. std normalisation')
    a = ga('default', [1, 0, 0, 0], std=True)
    s = math.sqrt(sum(x * x for x in a) / 4)
    ck(abs(s - 1) < 1e-12, 'default, std=True: unit population std')
    a0 = ga('passk', [1, 0, 0, 0, 0, 0, 0, 0], k=4); a1 = ga('passk', [1, 0, 0, 0, 0, 0, 0, 0], k=4, std=True)
    ck(close([x / math.sqrt(0.25) for x in a0], a1), 'passk, std=True: divided by sigma = sqrt(Rbar (1 - Rbar))')
    ck(close(ga('default', [0] * 4, std=True), [0.0] * 4), 'all-fail with std stays zero (no division by 0)')

    print('FAIL' if FAIL else 'PASS', f'({len(FAIL)} failures)')
    sys.exit(1 if FAIL else 0)


if __name__ == '__main__':
    main()
