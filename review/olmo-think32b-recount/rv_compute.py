"""Compute axis (reviewer): cumulative RL / pretraining at steps 100 / 750 / 2,300 from the pre-registered inputs
(Olmo 3 report as ledgered in rl-compute-share; the 32B Think RL script), own arithmetic."""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rv_core as C
import numpy as np
N, D = 3.2e10, 5.7e12                       # 32B; 5.5T + 0.1T midtraining + 0.1T long-context
PT = 6 * N * D
PT_GPUH = (9.5 * 512 + 35 * 1024) * 24       # report: 9.5 d on 512 + 35 d on 1,024 H100
gpuh = lambda s: (5 * 24 * 224) * min(s, 750) / 750 + (21 * 24 * 224) * max(s - 750, 0) / 1550
rs = C.rows(); head = {p["pid"] for p in C.problems()} - C.excluded()
mean_len = {m: float(np.mean([r["n_tok"] for r in rs if r["job"] == f"F_{m}" and r["pid"] in head])) for m in C.MODELS}
mean_len_all60 = {m: float(np.mean([r["n_tok"] for r in rs if r["job"] == f"F_{m}"])) for m in C.MODELS}
out = {"pretrain_flops": PT, "pretrain_gpuh": PT_GPUH, "mean_len_head": mean_len, "mean_len_all60": mean_len_all60}
for s, m in ((100, "s0100"), (750, "s0750"), (2300, "s2300")):
    low = s * 64 * 8 * 10000 * 8 * N / PT
    high = s * 128 * 8 * 32768 * 10 * N / PT
    mid_own = s * 128 * 8 * mean_len[m] * 8 * N / PT
    rl_models = ("s0100", "s0750", "s2300")
    mid_rlavg = s * 128 * 8 * np.mean([mean_len[x] for x in rl_models]) * 8 * N / PT
    out[f"step_{s}"] = {"flops_low": low, "flops_mid_own_len": mid_own, "flops_mid_rlavg_len": float(mid_rlavg),
                        "flops_high": high, "gpuh": gpuh(s), "gpuh_ratio": gpuh(s) / PT_GPUH}
json.dump(out, open(os.path.join(C.HERE, "out", "compute_axis.json"), "w"), indent=1)
print(f"pretrain 6ND = {PT:.4g}; pretrain GPU-h = {PT_GPUH:.4g}")
for k, v in out.items():
    if k.startswith("step"):
        print(k, {a: (f"{b:.3g}") for a, b in v.items()})
print("mean lengths (59):", {k: round(v) for k, v in mean_len.items()}, "(60):", {k: round(v) for k, v in mean_len_all60.items()})
