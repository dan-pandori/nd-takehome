"""Learning-rate schedules of the Olmo 3 stages, as stated in the sources listed in olmo_weights/steps_lr.md.

lr(family, stage, step) -> LR at that optimizer step of that stage (None where unknown). mean_lr(...) averages over
the steps of an interval (a, b]. Stage names: stage1, stage2, stage3, sft-1e-4, sft-5e-5, sft (7B), dpo, rl, rlzero.
"""
import math


def _cos(step, peak, warm, tmax, af=0.1):
    eta = peak * af
    if step < warm:
        return peak * step / warm
    if step >= tmax:
        return eta
    return eta + (peak - eta) * (1 + math.cos(math.pi * (step - warm) / (tmax - warm))) / 2


def _half_cos(step, peak, warm, tmax, af=0.1):
    """OLMo-core HalfCosWithWarmup (scheduler.py): the second half of a cosine after `warm` steps."""
    eta = peak * af
    if step < warm:
        return (eta + (peak - eta) / 2) * step / warm
    if step >= tmax:
        return eta
    cur, T = step - warm, tmax - warm
    cur += T
    T *= 2
    return eta + (peak - eta) * (1 + math.cos(math.pi * cur / T)) / 2


def _lin(step, peak, warm, tmax):
    """OLMo-core LinearWithWarmup with alpha_f = 0."""
    if step < warm:
        return peak * step / warm
    if step >= tmax:
        return 0.0
    return peak - peak * (step - warm) / (tmax - warm)


T32_S1 = 5.93e12 / 8388608          # report Fig. 4: cosine over one epoch of 5.93 T tokens (truncated at 656,000)
T7_S1A = 5e12 / 4194304             # 7B first half: cosine over 5 T tokens, until step 597,046
T7_S1B = 1413814                    # 7B second half stretched to one epoch, 5.93 T tokens (report Fig. 3)


def lr(family, stage, step):
    if family == "32B":
        if stage == "stage1":
            return _cos(step, 6e-4, 2000, T32_S1)
        if stage == "stage2":
            return _lin(step, 2.071e-4, 0, 23842)
        if stage == "stage3":
            return _lin(step, 2.071e-4, 200, 11921)
        if stage in ("sft-1e-4", "sft-5e-5"):
            peak = 1e-4 if stage == "sft-1e-4" else 5e-5
            return _lin(step, peak, round(0.03 * 10790), 10790)
        if stage == "dpo":
            return _lin(step, 7e-8, round(0.1 * 1563), 1563) if step else None
        if stage == "rl":
            return 2e-6
    if family == "7B":
        if stage == "stage1":
            return _cos(step, 3e-4, 2000, T7_S1A) if step < 597046 else _half_cos(step, 3e-4, 597046, T7_S1B)
        if stage == "stage2":
            return _lin(step, 2.074e-4, 0, 47684)
        if stage == "stage3":
            return _lin(step, 2.074e-4, 200, 11921)
        if stage == "sft":
            return _lin(step, 5e-5, round(0.03 * 43297), 43297)
        if stage == "dpo":
            return _lin(step, 8e-8, round(0.1 * 1172), 1172) if step else None
        if stage in ("rl", "rlzero"):
            return 1e-6
    return None


def mean_lr(family, stage, s0, s1, n=200):
    """Mean LR over optimizer steps s0+1 .. s1 (midpoint rule on n points)."""
    if s1 is None or s0 is None or s1 <= s0:
        return None
    vals = []
    for i in range(n):
        x = s0 + (i + 0.5) * (s1 - s0) / n
        v = lr(family, stage, x)
        if v is None:
            return None
        vals.append(v)
    return sum(vals) / len(vals)
