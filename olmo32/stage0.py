#!/usr/bin/env python3
"""Stage-0 summary (AIME 2024 pilot set; never an evaluation number): lengths, cut share, format checks, grades and
throughput of one Stage-0 job. Usage: stage0.py <job> <log> <usd_per_h> -> olmo32/stage0_summary.json (appends)."""
import json
import re
import subprocess
import sys
from pathlib import Path

import numpy as np

job, log, rate = sys.argv[1], sys.argv[2], float(sys.argv[3])
rows = [json.loads(ln) for ln in open(f"artifacts/olmo32/graded/{job}.jsonl")]
n_req = 240 if job == "s0_dpo" else len(rows)
tok = np.array([r["n_tok"] for r in rows])
cut = np.array([r["finish"] == "length" for r in rows])
te = np.array([bool(r["think_end"]) for r in rows])
rl = np.array([bool(r["rl"]) for r in rows])
fin = np.array([bool(r["final"]) for r in rows])
boxed = np.array([r.get("final_from") == "boxed" for r in rows])
integ = subprocess.run([sys.executable, "olmo32/vllm_log_tokens.py", log], capture_output=True, text=True).stdout.strip()
m = re.search(r"span (\d+) s, generated ~(\d+) tokens, mean (\d+) tok/s, mean resident ([0-9.]+)", integ)
span, gen, tps, res = (float(x) for x in m.groups())
out = {"job": job, "samples_requested": n_req, "samples_finished": len(rows), "unfinished": n_req - len(rows),
       "mean_tok_finished": round(float(tok.mean()), 1), "median_tok_finished": float(np.median(tok)),
       "cut_at_32768": int(cut.sum()), "cut_frac_finished": round(float(cut.mean()), 4),
       "mean_tok_bound_low": round(float(tok.sum() / len(rows)), 1),
       "mean_tok_bound_high": round(float((tok.sum() + 32768 * (n_req - len(rows))) / n_req), 1),
       "think_end_frac_uncut": round(float(te[~cut].mean()), 4) if (~cut).any() else None,
       "boxed_final_frac_of_think_end": round(float(boxed[te].mean()), 4) if te.any() else None,
       "pass1_rl_finished": round(float(rl.mean()), 4), "pass1_final_finished": round(float(fin.mean()), 4),
       "rl_final_disagree_frac": round(float((rl != fin).mean()), 4),
       "rl_not_final": int((rl & ~fin).sum()), "final_not_rl": int((fin & ~rl).sum()),
       "vllm_span_s": span, "vllm_generated_tokens": gen, "vllm_mean_tok_per_s": tps, "vllm_mean_resident": res,
       "usd_per_h": rate, "usd_per_mtok": round(rate / (tps * 3600 / 1e6), 3), "vllm_integral": integ}
print(json.dumps(out, indent=1))
with open("olmo32/stage0_summary.json", "a") as f:
    f.write(json.dumps(out) + "\n")
