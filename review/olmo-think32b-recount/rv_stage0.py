"""Stage 0 recount (reviewer) from my re-grade of s0_dpo plus the job's own vLLM log (own parser) and meta."""
import json, os, re, sys
from datetime import datetime
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rv_core as C
rs = [r for r in C.rows() if r["job"] == "s0_dpo"]
tok = np.array([r["n_tok"] for r in rs])
cut = [r for r in rs if r["finish"] == "length"]; unc = [r for r in rs if r["finish"] == "stop"]
diff = [r for r in rs if r["rl"] != r["final"]]
out = {"n": len(rs), "mean": float(tok.mean()), "median": float(np.median(tok)), "cut": len(cut),
       "cut_share": len(cut) / len(rs),
       "mean_fail_rl": float(np.mean([r["n_tok"] for r in rs if not r["rl"]])),
       "mean_correct_rl": float(np.mean([r["n_tok"] for r in rs if r["rl"]])),
       "uncut_think_end": float(np.mean([r["think_end"] for r in unc])),
       "uncut_boxed_after": float(np.mean([r["final_src"] == "boxed" for r in unc])),
       "pass1_rl": float(np.mean([r["rl"] for r in rs])), "pass1_final": float(np.mean([r["final"] for r in rs])),
       "rl_ne_final": len(diff), "rl_only": sum(r["rl"] and not r["final"] for r in diff),
       "rl_ne_final_by_finish": {f: sum(r["finish"] == f for r in diff) for f in ("stop", "length")},
       "rl_ne_final_src": [r["final_src"] for r in diff]}
pat = re.compile(r"INFO (\d\d-\d\d \d\d:\d\d:\d\d) .*Avg generation throughput: ([0-9.]+) tokens/s, Running: (\d+) reqs")
pts = [(datetime.strptime("2026-" + m.group(1), "%Y-%m-%d %H:%M:%S"), float(m.group(2)), int(m.group(3)))
       for m in (pat.search(l) for l in open(os.path.join(C.ROOT, "artifacts/olmo32/logs/q_s0_dpo.log"), errors="ignore")) if m]
integ = sum(b[1] * (b[0] - a[0]).total_seconds() for a, b in zip(pts, pts[1:]))
span = (pts[-1][0] - pts[0][0]).total_seconds()
meta = json.loads(open(os.path.join(C.ROOT, "artifacts/olmo32/meta/s0_dpo.json")).readline())
out.update({"log_points": len(pts), "log_span_s": span, "log_integral_tokens": integ, "log_tok_per_s": integ / span,
            "log_mean_running": float(np.mean([p[2] for p in pts])), "rows_tokens": int(tok.sum()),
            "meta_gen_tokens": meta["gen_tokens"], "meta_t_gen_s": meta["t_gen_s"],
            "rows_tok_per_s_over_t_gen": float(tok.sum() / meta["t_gen_s"])})
for rate in (5.29,):
    out[f"usd_per_Mtok_at_{rate}"] = rate / (out["log_tok_per_s"] * 3600) * 1e6
json.dump(out, open(os.path.join(C.HERE, "out", "stage0.json"), "w"), indent=1)
for k, v in out.items():
    print(k, round(v, 4) if isinstance(v, float) else v)
