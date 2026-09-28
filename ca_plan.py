#!/usr/bin/env python3
"""Run ckpt-avg: the variants, fixed before any evaluation (pre-registration/ckpt-avg.md).

Material: run stage1-dynamics' checkpoints (bucket stage1-dynamics/ckpts/sd), all 3,214,336-param
from-scratch `lean_seq` cap-6 GPTs.  WSD: lr 1e-3 constant after a 200-step warmup, then linear
decay to 1e-4 over the last 20 % of --steps.  So the 24k runs are stable up to step 19,200 and decay
19,200 -> 24,000; the W-12k branch decays 9,600 -> 12,000 and W-6k 4,800 -> 6,000 (both resumed from
the 24k run's saved states, so they share its stable prefix).
  arm W  seeds 0-7, data/p2/train_depth3_f0_a1.jsonl: w_s{k}.step{1000..23000}.pt (every 1,000),
         endpoints w_s{k}.pt (24k), w12_s{k}.pt, w6_s{k}.pt
  arm F  seeds 0-3, data/sd/train_fresh.jsonl: f_s{k}.step{2000..22000}.pt (every 2,000), f_s{k}.pt

Variants per run (R = w_s{k} or f_s{k}):
  E24/E12/E6        the decayed endpoints as stage1-dynamics reported them
  A{D}_K{K}         uniform average of the last K stable-phase trajectory checkpoints before decay
                    point D (i.e. at steps < 0.8 * D)
  T24_3, T24_5      average of the decayed 24k endpoint with its 2 / 4 preceding trajectory
                    checkpoints (all inside the 24k run's decay phase: across-decay averaging)
  LS6, LSd3         the run's checkpoint with the lowest half-A validation loss on the 6-line bin /
                    the depth-3 slice, among ALL its saved checkpoints (trajectory + endpoints)

  python3 ca_plan.py averages    -> '<name>\t<member>,<member>,...' (paths under ckpts/sd/)
  python3 ca_plan.py all_ckpts   -> every stage1-dynamics checkpoint this run touches
"""
import sys

W_SEEDS, F_SEEDS = range(8), range(4)


def runs():
    """(run stem, trajectory steps, endpoints dict)"""
    for k in W_SEEDS:
        yield f'w_s{k}', list(range(1000, 24000, 1000)), {'E24': f'w_s{k}', 'E12': f'w12_s{k}', 'E6': f'w6_s{k}'}
    for k in F_SEEDS:
        yield f'f_s{k}', list(range(2000, 24000, 2000)), {'E24': f'f_s{k}'}


def step_ck(stem, t):
    return f'{stem}.step{t:05d}'


def averages():
    out = {}
    for stem, steps, ends in runs():
        for D, Ks in ((24000, (2, 4, 8)), (12000, (2, 4, 8)), (6000, (2, 4))):
            if f'E{D // 1000}' not in ends:
                continue
            stable = [t for t in steps if t < 0.8 * D]
            for K in Ks:
                if K <= len(stable):
                    out[f'{stem}.A{D // 1000}_K{K}'] = [step_ck(stem, t) for t in stable[-K:]]
        tail = [t for t in steps if t > 0.8 * 24000]
        for n in (3, 5):
            if n - 1 <= len(tail):
                out[f'{stem}.T24_{n}'] = [step_ck(stem, t) for t in tail[-(n - 1):]] + [ends['E24']]
    # control: a checkpoint averaged with itself must reproduce that checkpoint's evaluation exactly
    out['w_s0.CTRL_self19000'] = [step_ck('w_s0', 19000)] * 2
    return out


def candidates(stem):
    """Everything LS may select from, for one run."""
    for s, steps, ends in runs():
        if s == stem:
            return [step_ck(stem, t) for t in steps] + list(ends.values())
    raise KeyError(stem)


def all_ckpts():
    return [c for stem, _, _ in runs() for c in candidates(stem)]


if __name__ == '__main__':
    if sys.argv[1] == 'averages':
        for k, v in averages().items():
            print(f'{k}\t{",".join(v)}')
    elif sys.argv[1] == 'all_ckpts':
        print('\n'.join(all_ckpts()))
