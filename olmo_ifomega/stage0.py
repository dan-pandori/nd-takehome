#!/usr/bin/env python3
"""Stage-0 summary (stage0_problems.jsonl; never an evaluation number): per task lengths, cut share, `</think>` share,
grade rates and agreement; job throughput from the vLLM log integral (olmo32/vllm_log_tokens.py) and the job meta.
Usage: stage0.py <job> <log> <usd_per_h> -> olmo_ifomega/stage0_summary.json (appends one line)."""
import json
import re
import subprocess
import sys
from collections import defaultdict

import numpy as np

job, log, rate = sys.argv[1], sys.argv[2], float(sys.argv[3])
rows = [json.loads(ln) for ln in open(f"artifacts/olmo_ifomega/graded/{job}.jsonl")]
meta = [json.loads(ln) for ln in open(f"artifacts/olmo_ifomega/meta/{job}.json")][-1]
by = defaultdict(list)
for r in rows:
    by[r["task"]].append(r)
tasks = {}
for t, rs in sorted(by.items()):
    tok = np.array([r["n_tok"] for r in rs])
    cut = np.array([r["finish"] == "length" for r in rs])
    d = {"n": len(rs), "mean_tok": round(float(tok.mean()), 1), "median_tok": float(np.median(tok)),
         "p90_tok": float(np.percentile(tok, 90)), "cut_frac": round(float(cut.mean()), 4),
         "think_end_frac": round(float(np.mean([bool(r["think_end"]) for r in rs])), 4),
         "think_end_frac_uncut": round(float(np.mean([bool(r["think_end"]) for r in rs if r["finish"] != "length"])), 4)
         if (~cut).any() else None}
    for g in ("strict", "loose", "rlview", "omega", "rl", "doubly"):
        if g in rs[0]:
            d[f"pass1_{g}"] = round(float(np.mean([bool(r[g]) for r in rs])), 4)
    if "omega" in rs[0]:
        d["omega_ne_rl"] = int(sum(bool(r["omega"]) != bool(r["rl"]) for r in rs))
        d["rl_not_omega"] = int(sum(bool(r["rl"]) and not r["omega"] for r in rs))
        d["omega_not_rl"] = int(sum(bool(r["omega"]) and not r["rl"] for r in rs))
    if "strict" in rs[0]:
        d["strict_ne_rlview"] = int(sum(bool(r["strict"]) != bool(r["rlview"]) for r in rs))
    tasks[t] = d
integ = subprocess.run([sys.executable, "olmo_ifomega/vllm_log_tokens.py", log], capture_output=True, text=True).stdout.strip()
m = re.search(r"span (\d+) s, generated ~(\d+) tokens, mean (\d+) tok/s, mean resident ([0-9.]+)", integ)
span, gen, tps, res = (float(x) for x in m.groups()) if m else (0, 0, 0, 0)
out = {"job": job, "model": meta["name"], "samples": len(rows), "gen_tokens": meta["gen_tokens"],
       "t_load_s": meta["t_load_s"], "t_gen_s": meta["t_gen_s"], "tok_per_s_job": meta["tok_per_s"],
       "vllm_span_s": span, "vllm_tok_per_s": tps, "vllm_mean_resident": res, "gpus": meta["gpus"],
       "usd_per_h": rate, "usd_per_mtok_job": round(rate / (meta["tok_per_s"] * 3600 / 1e6), 3), "tasks": tasks}
print(json.dumps(out, indent=1))
with open("olmo_ifomega/stage0_summary.json", "a") as f:
    f.write(json.dumps(out) + "\n")
