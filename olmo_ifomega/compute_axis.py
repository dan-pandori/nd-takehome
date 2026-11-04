#!/usr/bin/env python3
"""Cumulative RL compute / pretraining compute at the Olmo 3.1 Think 32B checkpoints (x-axis of the reach figure).

olmo32/compute_axis.py (run olmo-think32b), unchanged except the output path; run it with olmo32/lengths.csv for
olmo-think32b's middle estimate (AIME lengths) and with olmo_ifomega/lengths_mix.csv for this run's (RL's prompt mix:
30 % maths at the OMEGA test_out length, 29 % IF at the IFBench length, 41 % code + chat at the mean of the two).

Inputs (nd-rl docs/literature/2026-10-19-rl-compute-share, compute_table.csv rows "Olmo 3 Think 32B (final RL)" and
"Olmo 3.1 Think 32B (RL +21 days)", and the 7B pilot memo olmo_pilot/decision_32b.md):
  pretraining FLOPs 6 N D with N = 3.2e10, D = 5.7e12 (5.5T pretraining + 0.1T midtraining + 0.1T long context)
  pretraining GPU-hours 9.5 d x 512 + 35 d x 1,024 = 976,896
  RL: 8 samples per prompt, 32,768-token responses; unique prompts per step 64 (open-instruct
      scripts/train/olmo3/32b_think_rl.sh at 7e780f2fea, --num_unique_prompts_rollout 64) or 128 (paper App. Table 49)
  RL GPU-hours: steps 1-750 ~5 days x 224 GPUs (paper S2: "approximately 5 days"), steps 751-2,300 21 days x 224 GPUs
      (paper S2: "continued our best RL run for another 21 days on 224 GPUs"); linear in steps within each phase.
RL FLOPs per step = prompts x 8 x L x (2N rollout + 6N training + 2N x extra_fwd), L = mean response tokens:
  low    = 64 prompts, L = 10,000 (paper: mean response > 10K), extra_fwd 0
  high   = 128 prompts, L = 32,768 (the cap), extra_fwd 1 (old-policy / reference log-probs)
  middle = 128 prompts, L = this run's measured mean AIME response length of the checkpoint (interpolated
           linearly in steps between measured checkpoints, from the DPO checkpoint at step 0), extra_fwd 0
Usage: compute_axis.py [<lengths.csv: step,mean_tok>] -> olmo_ifomega/compute_axis.csv
"""
import csv
import sys

import numpy as np

N, D = 3.2e10, 5.7e12
PRE = 6 * N * D
PRE_GPUH = 9.5 * 24 * 512 + 35 * 24 * 1024
GPUH_750, GPUH_EXT = 5 * 24 * 224, 21 * 24 * 224
STEPS = (100, 750, 2300)


def gpuh(s):
    return s / 750 * GPUH_750 if s <= 750 else GPUH_750 + (s - 750) / 1550 * GPUH_EXT


def flops(s, prompts, L, extra):
    return s * prompts * 8 * L * (2 * N + 6 * N + 2 * N * extra)


def main():
    meas = {}
    if len(sys.argv) > 1:
        meas = {int(r["step"]): float(r["mean_tok"]) for r in csv.DictReader(open(sys.argv[1]))}
    rows = []
    for s in STEPS:
        lo, hi = flops(s, 64, 10000, 0), flops(s, 128, 32768, 1)
        r = {"step": s, "rl_flops_low": f"{lo:.3e}", "rl_flops_high": f"{hi:.3e}", "ratio_low": f"{lo / PRE:.3e}",
             "ratio_high": f"{hi / PRE:.3e}", "ratio_geomean": f"{(lo * hi) ** 0.5 / PRE:.3e}"}
        if meas:
            st = sorted(meas)
            grid = np.arange(1, s + 1)
            L = np.interp(grid, st, [meas[k] for k in st])
            mid = float(np.sum(128 * 8 * L * 8 * N))
            r.update({"rl_flops_mid": f"{mid:.3e}", "ratio_mid": f"{mid / PRE:.3e}"})
        r.update({"rl_gpu_hours": round(gpuh(s)), "gpu_hour_ratio": f"{gpuh(s) / PRE_GPUH:.4f}"})
        rows.append(r)
    with open("olmo_ifomega/compute_axis.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    print(f"pretraining 6ND = {PRE:.3e} FLOPs, {PRE_GPUH:,.0f} GPU-h")
    for r in rows:
        print(r)


if __name__ == "__main__":
    main()
