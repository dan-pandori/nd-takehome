"""Reviewer (olmo-weights), phase 2: numbers in the write-up not covered by the phase-1 recount.
(1) per-stage median r/step ÷ LR for stages 1-3 (my implementation of the cited schedules, mean LR over each interval);
(2) per-module r / overall r by stage, and DPO's jump by module; (3) straightness on the executor's chain endpoints and
exclusions; (4) 7B stage-1 1,000-step interval count. Usage: python3 rv_phase2_checks.py ROOT"""
import csv, gzip, math, os, statistics as st, sys
from collections import defaultdict
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
ROOT = sys.argv[1]
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out")
rows = list(csv.DictReader(open(f"{OUT}/rv_intervals.csv")))
mods = list(csv.DictReader(gzip.open(f"{OUT}/rv_modules.csv.gz", "rt")))

def lr32_s1(t):
    W, T, peak = 2000, 5.93e12 / 8388608, 6e-4
    if t < W: return peak * t / W
    return 0.1 * peak + 0.9 * peak * (1 + math.cos(math.pi * (t - W) / (T - W))) / 2
def lr7_s1(t):
    W, peak = 2000, 3e-4
    T1 = int(5e12) // 4194304          # first cosine (5 T), used up to step 597,046
    if t < W: return peak * t / W
    if t <= 597046:
        return 0.1 * peak + 0.9 * peak * (1 + math.cos(math.pi * (t - W) / (T1 - W))) / 2
    # HalfCosWithWarmup(warmup = T1 // 2 + W // 2): second half of a cosine stretched to end at one epoch
    w2 = T1 // 2 + W // 2; T = 1413814
    c, tm = t - w2, T - w2
    c += tm; tm *= 2
    return 0.1 * peak + 0.9 * peak * (1 + math.cos(math.pi * c / tm)) / 2
def lin(peak, W, T):
    return lambda t: peak * t / W if (W and t < W) else peak * max(T - t, 0) / (T - W)
LR = {("32B", "s1"): lr32_s1, ("7B", "s1"): lr7_s1,
      ("32B", "s2i1"): lin(2.071235285e-4, 0, 23842), ("32B", "s2i2"): lin(2.071235285e-4, 0, 23842),
      ("32B", "s3"): lin(2.071235285e-4, 200, 11921), ("7B", "s2"): lin(2.0712352850360292e-4, 0, 47684),
      ("7B", "s3"): lin(2.0712352850360292e-4, 200, 11921)}
print("(1) median r/step / LR, 1,000-step within-stage intervals")
for job, chain, key in (("b32_s1", "stage1-sampled", ("32B", "s1")), ("b32_s2", "ingredient1", ("32B", "s2i1")),
                        ("b32_s2", "ingredient2", ("32B", "s2i2")), ("b32_s3", "stage3", ("32B", "s3")),
                        ("b7_s1", "stage1-sampled", ("7B", "s1")), ("b7_s2", "stage2", ("7B", "s2")),
                        ("b7_s3", "stage3", ("7B", "s3"))):
    f = LR[key]; v = []; v1000 = []
    for r in rows:
        if r["job"] == job and r["chain"] == chain and r["kind"] == "within":
            a, b = int(r["a"].split("/")[-1]), int(r["b"].split("/")[-1])
            m = float(np.mean([f(t) for t in range(a + 1, b + 1)]))
            x = float(r["r_per_step"]) / m
            v.append(x)
            if b - a == 1000 and not (job.startswith("b") and "s1" in job and False):
                v1000.append(x)
    print(f"  {job:7s} {chain:15s} n={len(v):3d} median {st.median(v):.3f}  (1,000-step only n={len(v1000)} median {st.median(v1000) if v1000 else float('nan'):.3f})")
# 7B stage-1 intervals of exactly 1,000 steps: pairs vs gaps that happen to be 1,000
s1 = [r for r in rows if r["job"] == "b7_s1"]
print("(4) 7B stage-1: members", len(s1) + 1, "| intervals of 1,000 steps", sum(int(r["n_steps"] or 0) == 1000 for r in s1),
      "| other", [(r["a"].split("/")[-1], r["b"].split("/")[-1]) for r in s1 if int(r["n_steps"] or 0) != 1000][:6], "...")
# (2) module ratio r_module / r_all per interval, median over within intervals per chain
print("(2) median over within intervals of r_module / r_all")
rall = {(r["job"], r["chain"], r["idx"]): float(r["r"]) for r in rows}
kind = {(r["job"], r["chain"], r["idx"]): r["kind"] for r in rows}
g = defaultdict(lambda: defaultdict(list))
for m in mods:
    k = (m["job"], m["chain"], m["idx"])
    if kind.get(k) == "within" and m["r"]:
        g[(m["job"], m["chain"])][m["module"]].append(float(m["r"]) / rall[k])
order = ["q", "k", "v", "o", "gate", "up", "down", "embed", "lm_head", "q_norm", "k_norm", "post_attn_norm", "post_ff_norm", "final_norm"]
print("  " + " ".join(f"{x[:7]:>7s}" for x in order))
for key in sorted(g):
    print(f"  {key[0]:7s} {key[1][:12]:12s}", " ".join(f"{st.median(g[key][x]):7.2f}" for x in order))
for job, chain in (("p32_sft", "sftmain-to-dpo"), ("p7_sft", "sft-dpo")):
    idx = [r["idx"] for r in rows if r["job"] == job and r["chain"] == chain and r["b"].endswith("/dpo")][0]
    d = {m["module"]: float(m["r"]) / rall[(job, chain, idx)] for m in mods if (m["job"], m["chain"], m["idx"]) == (job, chain, idx) and m["r"]}
    print(f"  DPO jump {job}:", " ".join(f"{x}={d[x]:.2f}" for x in order))
