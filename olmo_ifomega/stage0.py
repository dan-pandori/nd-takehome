#!/usr/bin/env python3
"""Stage-0 summary (stage0_problems.jsonl; never an evaluation number): per task lengths, cut share, `</think>` share,
grade rates and agreement; job throughput from the vLLM log integral (olmo32/vllm_log_tokens.py) and the job meta.
Usage: stage0.py <job> <log> <usd_per_h> <samples_per_prompt> -> olmo_ifomega/stage0_summary.json (appends)."""
import json
import re
import subprocess
import sys
from collections import defaultdict

import numpy as np
from pathlib import Path

job, log, rate = sys.argv[1], sys.argv[2], float(sys.argv[3])
rows = [json.loads(ln) for ln in open(f"artifacts/olmo_ifomega/graded/{job}.jsonl")]
mf = Path(f"artifacts/olmo_ifomega/meta/{job}.json")
# a job stopped at the Stage-0 cap writes no meta: censored, the vLLM log integral stands in for its totals
meta = [json.loads(ln) for ln in open(mf)][-1] if mf.exists() else None
probs = [json.loads(ln) for ln in open("olmo_ifomega/stage0_problems.jsonl")]
n_req = {t: 0 for t in {p["task"] for p in probs}}
for p in probs:
    n_req[p["task"]] += int(sys.argv[4]) if len(sys.argv) > 4 else 0
by = defaultdict(list)
for r in rows:
    by[r["task"]].append(r)
tasks = {}
for t, rs in sorted(by.items()):
    tok = np.array([r["n_tok"] for r in rs])
    cut = np.array([r["finish"] == "length" for r in rs])
    d = {"n": len(rs), "n_requested": n_req.get(t, 0), "mean_tok": round(float(tok.mean()), 1), "median_tok": float(np.median(tok)),
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
m0 = meta or {}
out = {"job": job, "model": rows[0]["model"], "samples": len(rows), "censored": meta is None,
       "gen_tokens_finished": int(sum(r["n_tok"] for r in rows)), "gen_tokens_vllm": gen,
       "t_load_s": m0.get("t_load_s"), "t_gen_s": m0.get("t_gen_s"), "tok_per_s_job": m0.get("tok_per_s"),
       "vllm_span_s": span, "vllm_tok_per_s": tps, "vllm_mean_resident": res, "gpus": m0.get("gpus"),
       "usd_per_h": rate, "usd_per_mtok_vllm": round(rate / (tps * 3600 / 1e6), 3) if tps else None, "tasks": tasks}
print(json.dumps(out, indent=1))
with open("olmo_ifomega/stage0_summary.json", "a") as f:
    f.write(json.dumps(out) + "\n")
