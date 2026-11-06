"""Compute axis and per-job compute (reviewer, olmo-ifomega).

Axis: cumulative RL / pretraining at steps 100 / 750 / 2,300 with the pre-registered inputs (olmo-think32b's
definitions: N = 3.2e10, D = 5.7e12, PT = 6ND; pretraining 9.5 d x 512 + 35 d x 1,024 GPUs; RL 5 d x 224 GPUs to step
750, then 21 d x 224 to 2,300, linear in steps; FLOPs per step = prompts x 8 x L x (8N + 2N x extra_fwd);
low 64 prompts, L 10,000, extra 0; high 128 prompts, L 32,768, extra 1). Middle: 128 prompts, extra 0, L per
checkpoint = RL's prompt mix (Dolci-Think-RL-32B: 30.2k maths, 29.8k IF, 42.0k code + chat of 102,026) of my
fixed-phase means: maths at the OMEGA test_out mean, IF at the IFBench (all 300) mean, code + chat at the mean of
the two; interpolated linearly in steps from dpo (step 0); s0100 has no OMEGA run, so its maths length is
interpolated between dpo and s0750.
Per job: samples and generated tokens counted from the rows (exact); load + generation seconds of the meta segment(s)
(a job resumed on another pod has only its last segment in meta: flagged when rows != meta samples).
Output: out/compute.json, out/compute.txt"""
import json
import os
from collections import defaultdict

import numpy as np

import rv_core as C

N, D = 3.2e10, 5.7e12
PT = 6 * N * D
PT_GPUH = (9.5 * 512 + 35 * 1024) * 24


def gpuh(s):
    return (5 * 24 * 224) * min(s, 750) / 750 + (21 * 24 * 224) * max(s - 750, 0) / 1550


def main():
    st = json.load(open(os.path.join(C.OUT, "stats.json")))
    Lif = {m: v["mean_tok"] for m, v in st["ifbench|all"]["lengths_fixed"].items()}
    Lom = {m: v["mean_tok"] for m, v in st["omega_out|headline"]["lengths_fixed"].items()}
    Lom["s0100"] = Lom["dpo"] + (Lom["s0750"] - Lom["dpo"]) * 100 / 750
    fm, fi = 30.2 / 102.026, 29.8 / 102.026
    mix = {m: fm * Lom[m] + fi * Lif[m] + (1 - fm - fi) * (Lom[m] + Lif[m]) / 2 for m in Lif}
    steps = {"dpo": 0, "s0100": 100, "s0750": 750, "s2300": 2300}
    xs = [steps[m] for m in ("dpo", "s0100", "s0750", "s2300")]
    ys = [mix[m] for m in ("dpo", "s0100", "s0750", "s2300")]
    out = {"PT": PT, "PT_GPUH": PT_GPUH, "L_if": Lif, "L_omega_out": Lom, "L_mix": mix, "axis": {}}
    txt = [f"PT {PT:.4g} FLOPs, {PT_GPUH:,.0f} GPU-h; L_mix {json.dumps({k: round(v) for k, v in mix.items()})}"]
    for s in (100, 750, 2300):
        lo = s * 64 * 8 * 10000 * 8 * N / PT
        hi = s * 128 * 8 * 32768 * 10 * N / PT
        grid = np.arange(1, s + 1)
        L = np.interp(grid, xs, ys)
        mid = float(np.sum(128 * 8 * L * 8 * N)) / PT
        out["axis"][s] = {"ratio_low": lo, "ratio_mid": mid, "ratio_high": hi, "ratio_geomean": (lo * hi) ** 0.5,
                          "gpuh": gpuh(s), "gpuh_ratio": gpuh(s) / PT_GPUH}
        txt.append(f"step {s}: low {lo:.3e} mid {mid:.3e} high {hi:.3e} geomean {(lo * hi) ** .5:.3e}"
                   f" GPU-h {gpuh(s):,.0f} ratio {gpuh(s) / PT_GPUH:.4f}")
    # per job
    meta = defaultdict(list)
    for f in os.listdir(os.path.join(C.ART, "meta")):
        if f.endswith(".json"):
            for ln in open(os.path.join(C.ART, "meta", f)):
                if ln.strip():
                    m = json.loads(ln)
                    meta[m["job"]].append(m)
    jobs = {}
    for job in C.jobs():
        rows = C.load_regrade(job)
        segs = meta.get(job, [])
        jobs[job] = {"samples": len(rows), "gen_tokens": sum(r["n_tok"] for r in rows),
                     "cut": sum(r["finish"] == "length" for r in rows),
                     "meta_segments": len(segs), "meta_samples": sum(m["samples"] for m in segs),
                     "meta_tokens": sum(m["gen_tokens"] for m in segs),
                     "meta_seconds": round(sum(m["t_load_s"] + m["t_gen_s"] for m in segs), 1),
                     "gpus": sorted({g for m in segs for g in m.get("gpus", [])})}
        j = jobs[job]
        flag = "" if j["samples"] == j["meta_samples"] else "  (rows != meta samples: earlier segment(s) not in meta)"
        txt.append(f"{job:18s} samples {j['samples']:6d} tokens {j['gen_tokens']:11,d} cut {j['cut']:4d} meta segs"
                   f" {j['meta_segments']} meta samples {j['meta_samples']:6d} meta s {j['meta_seconds']:9.1f}{flag}")
    tot = {"samples": sum(j["samples"] for j in jobs.values()), "gen_tokens": sum(j["gen_tokens"] for j in jobs.values()),
           "meta_seconds": sum(j["meta_seconds"] for j in jobs.values())}
    txt.append("TOTAL " + json.dumps(tot))
    out["jobs"] = jobs
    out["total"] = tot
    json.dump(out, open(os.path.join(C.OUT, "compute.json"), "w"), indent=1)
    open(os.path.join(C.OUT, "compute.txt"), "w").write("\n".join(txt) + "\n")
    print("\n".join(txt))


if __name__ == "__main__":
    main()
