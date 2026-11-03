#!/usr/bin/env python3
"""Cumulative RL compute / pretraining compute at each RL-Zero checkpoint (x-axis of the reach figure).

Definitions follow nd-rl docs/literature/2026-10-19-rl-compute-share (its Olmo 3 7B RL-Zero row):
  pretraining FLOPs = 6 N D, N = 7.3e9, D = 6.08e12 (5.93T pretraining + 0.10T midtraining + 0.05T long context).
  RL FLOPs per step = rollout tokens x 2N x oversample + trained tokens x 6N + trained tokens x 2N x extra_fwd,
  rollout tokens = trained tokens = prompts_per_step x group x mean response length (prompt tokens added to the
  trained tokens in the high bound).
Olmo 3.1 RL-Zero-Math (open-instruct 7b_rlzero_math.sh, PR #1261): 32 prompts x 8 samples per step.
Mean response length L(s) is interpolated linearly in s between measured checkpoints:
  low bound  = measured mean on RL training prompts (Dolci probe), oversample 1, extra_fwd 0, no prompt tokens;
  high bound = measured mean on the AIME evaluation samples, oversample `--over_hi` (active sampling regenerates
               zero-variance groups), extra_fwd 1, prompt tokens included.
Input: a CSV with columns step, len_train, len_eval (mean response tokens per checkpoint; step 0 = base).
Usage: compute_axis.py <lengths.csv> <out.csv> [--over_hi 3] [--prompt_tok 180]
"""
import argparse
import csv

import numpy as np

N, D = 7.3e9, 6.08e12
PRE = 6 * N * D
PROMPTS, GROUP = 32, 8


def cum_flops(steps, lens, s_query, over, extra, prompt_tok):
    grid = np.arange(0, max(s_query) + 1)
    L = np.interp(grid, steps, lens)
    per_step = PROMPTS * GROUP * ((L) * 2 * N * over + (L + prompt_tok) * 6 * N + (L + prompt_tok) * 2 * N * extra)
    cum = np.concatenate([[0.0], np.cumsum(per_step[1:])])  # steps 1..s
    return {s: float(cum[s]) for s in s_query}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("lengths")
    ap.add_argument("out")
    ap.add_argument("--over_hi", type=float, default=3.0)
    ap.add_argument("--prompt_tok", type=float, default=180.0)
    a = ap.parse_args()
    rows = list(csv.DictReader(open(a.lengths)))
    steps = [int(r["step"]) for r in rows]
    lt = [float(r["len_train"]) for r in rows]
    le = [float(r["len_eval"]) for r in rows]
    q = steps
    lo = cum_flops(steps, lt, q, 1.0, 0, 0.0)
    hi = cum_flops(steps, le, q, a.over_hi, 1, a.prompt_tok)
    with open(a.out, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["step", "rl_flops_low", "rl_flops_high", "ratio_low", "ratio_high", "ratio_geomean"])
        for s in q:
            r_lo, r_hi = lo[s] / PRE, hi[s] / PRE
            w.writerow([s, f"{lo[s]:.3e}", f"{hi[s]:.3e}", f"{r_lo:.3e}", f"{r_hi:.3e}",
                        f"{(r_lo * r_hi) ** 0.5:.3e}" if r_lo > 0 else "0"])
    print(f"pretraining FLOPs 6ND = {PRE:.3e}; wrote {a.out}")


if __name__ == "__main__":
    main()
