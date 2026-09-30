#!/usr/bin/env python3
"""Group advantages for GRPO (run `grpo-state`), one function per variant behind one flag (`--adv`).  Pure Python, no
torch, so the unit tests (tests/test_grpo_adv.py) run anywhere.

Every function takes one group -- the G rollouts of one theorem from the same start state -- and returns G advantages.
`R` is the list of binary rewards (1 = Lean accepts the literal proof).

  default   A_i = R_i - mean(R)                                                   (grpo.py:117, run 4)
  unlikely  r_i = R_i (1 - beta_rank (G - rank_i) / G), A_i = r_i - mean(r)       He et al. 2506.02355v2 §4.1
            rank_i = 0-based rank of rollout i among the G by sequence log-prob under the sampling policy, most likely
            first (so the most likely correct proof keeps 1 - beta_rank, the least likely 1 - beta_rank / G); ranks are
            over all G rollouts, as the formula's normalisation by G implies (failures stay at 0 whatever their rank).
            Groups whose *unperturbed* advantage is zero (all fail / all succeed) stay at zero, as in the paper
            (nd-rl lit note he2025-rewarding-unlikely: "samples with zero advantage before the perturbation are still
            skipped").
  passk     Chen et al. 2508.10751v1 §2.4, analytic: with c = #correct, n = G,
              Rbar = 1 - C(n-c, k) / C(n, k)                        (expected pass@k of a random k-subset)
              A_pos = 1 - Rbar,  A_neg = 1 - Rbar - C(n-c-1, k-1) / C(n-1, k-1)
            = the mean over the k-subsets containing i of (max reward of the subset - Rbar); sums to zero over the
            group; k = 1 gives `default` exactly.  Chen et al. divide by sigma = sqrt(Rbar (1 - Rbar)); here that is
            `std=True` (applied to every variant alike), off by default so all variants share `default`'s scale.
            PKPO (2505.15201v5, Eq. 8) is the same pass@k gradient up to a per-group baseline and scale.
  distinct  r_i = R_i + bonus * novel_i / m_i, A_i = r_i - mean(r): a correct rollout whose (start-index-normalised)
            proof is new for this theorem -- not in the proofs found during training before this step -- earns
            `bonus`, split over its m_i copies in the group.  Unlike the others it can move an all-correct group.

std=True divides every nonzero group by its population standard deviation of the shaped rewards (the GRPO
normalisation; for passk this is Chen et al.'s sigma).
"""
import math

VARIANTS = ('default', 'unlikely', 'passk', 'distinct')


def _center(r):
    m = sum(r) / len(r)
    return [x - m for x in r]


def _comb(n, k):
    return math.comb(n, k) if 0 <= k <= n else 0


def adv_default(R):
    return _center([float(x) for x in R])


def adv_unlikely(R, logp, beta_rank=0.25):
    G = len(R)
    if all(R) or not any(R):
        return [0.0] * G
    order = sorted(range(G), key=lambda i: (-logp[i], i))     # most likely first; ties by index
    rank = [0] * G
    for rk, i in enumerate(order):
        rank[i] = rk
    return _center([R[i] * (1.0 - beta_rank * (G - rank[i]) / G) for i in range(G)])


def adv_passk(R, k=4):
    n = len(R); c = sum(1 for x in R if x)
    assert 1 <= k <= n, f'pass@k advantage needs 1 <= k <= group size ({k}, {n})'
    rbar = 1.0 - _comb(n - c, k) / _comb(n, k)
    a_pos = 1.0 - rbar
    a_neg = 1.0 - rbar - _comb(n - c - 1, k - 1) / _comb(n - 1, k - 1) if n > 1 else 0.0
    return [a_pos if x else a_neg for x in R]


def adv_distinct(R, novel_keys, bonus=0.5):
    """novel_keys[i]: a hashable key (the normalised proof) if rollout i is correct and new for the theorem, else None."""
    m = {}
    for kk in novel_keys:
        if kk is not None:
            m[kk] = m.get(kk, 0) + 1
    return _center([float(R[i]) + (bonus / m[novel_keys[i]] if novel_keys[i] is not None else 0.0) for i in range(len(R))])


def _std(r):
    mu = sum(r) / len(r)
    return math.sqrt(sum((x - mu) ** 2 for x in r) / len(r))


def group_advantages(kind, R, logp=None, novel_keys=None, k=4, beta_rank=0.25, bonus=0.5, std=False):
    if kind == 'default':
        a = adv_default(R)
    elif kind == 'unlikely':
        a = adv_unlikely(R, logp, beta_rank)
    elif kind == 'passk':
        a = adv_passk(R, k)
    elif kind == 'distinct':
        a = adv_distinct(R, novel_keys, bonus)
    else:
        raise ValueError(kind)
    a = [0.0 if abs(x) < 1e-12 else x for x in a]
    if std and any(a):
        if kind == 'passk':        # Chen et al.'s sigma: the std of the pass@k reward of a random k-subset
            n = len(R); c = sum(1 for x in R if x)
            rbar = 1.0 - _comb(n - c, k) / _comb(n, k)
            s = math.sqrt(rbar * (1 - rbar))
        else:
            s = _std([x for x in a])
        if s > 0:
            a = [x / s for x in a]
    return a
