#!/usr/bin/env python3
"""step_0100 was sampled on a seeded random half of the 90 problems (plan/F_s0100_half.txt; budget rule, log.md
2026-11-03). This puts every checkpoint on that same subset (headline problems only): pass@1 and pass@8 with
problem-bootstrap 95 % CIs, and expected entries / exits vs the base at k = 8. Reads olmo_pilot/results.csv.
Writes olmo_pilot/half_subset.csv and prints it."""
import csv
import math
from pathlib import Path

import numpy as np

O = Path("olmo_pilot")


def pk(n, c, k):
    n, c = int(n), int(c)
    if k > n:
        return float("nan")
    return 1.0 if n - c < k else 1 - math.comb(n - c, k) / math.comb(n, k)


def main():
    res = {(r["model"], r["pid"]): r for r in csv.DictReader(open(O / "results.csv"))}
    half = set(open(O / "plan" / "F_s0100_half.txt").read().split())
    pids = sorted(p for p in half if ("step_0100", p) in res and not res[("step_0100", p)]["excluded"])
    rng = np.random.default_rng(0)
    idx = rng.integers(0, len(pids), size=(10000, len(pids)))
    out = []
    for m in ("base", "step_0100", "step_0500", "step_2800"):
        row = {"model": m, "n_problems": len(pids)}
        for k in (1, 8):
            v = np.array([pk(res[(m, p)]["n_fixed"], res[(m, p)]["succ_fixed_rl"], k) for p in pids])
            lo, hi = np.percentile(v[idx].mean(1), [2.5, 97.5])
            row[f"pass@{k}"] = f"{v.mean():.3f} [{lo:.3f}, {hi:.3f}]"
        if m != "base":
            ent = ext = 0.0
            for p in pids:
                b = pk(res[("base", p)]["n_fixed"], res[("base", p)]["succ_fixed_rl"], 8)
                c = pk(res[(m, p)]["n_fixed"], res[(m, p)]["succ_fixed_rl"], 8)
                ent += c * (1 - b)
                ext += b * (1 - c)
            row["exp_entries_k8"], row["exp_exits_k8"] = round(ent, 2), round(ext, 2)
            row["mean_tok"] = round(np.mean([float(res[(m, p)]["mean_tok"]) for p in pids]))
        out.append(row)
    keys = ["model", "n_problems", "pass@1", "pass@8", "exp_entries_k8", "exp_exits_k8", "mean_tok"]
    with open(O / "half_subset.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=keys)
        w.writeheader()
        w.writerows(out)
    for r in out:
        print(r)


if __name__ == "__main__":
    main()
