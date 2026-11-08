#!/usr/bin/env python3
"""Stage-0 summary (never an evaluation number): per job, lengths, cut share, stop reasons, format flags, grades.

Usage: stage0.py <job> [<job> ...]  (reads artifacts/olmo_rlzero_if/{samples,graded,meta}/<job>.*)
"""
import gzip
import json
import sys
from pathlib import Path

import numpy as np

A = Path("artifacts/olmo_rlzero_if")


def main():
    out = {}
    for job in sys.argv[1:]:
        S = [json.loads(l) for l in gzip.open(A / "samples" / f"{job}.jsonl.gz", "rt")]
        G = {(r["pid"], r["chunk"], r["i"]): r for r in map(json.loads, open(A / "graded" / f"{job}.jsonl"))}
        meta = [json.loads(l) for l in open(A / "meta" / f"{job}.json")][-1] if (A / "meta" / f"{job}.json").exists() else {}
        L = np.array([r["n_tok"] for r in S])
        d = {"samples": len(S), "mean_tok": round(float(L.mean())), "median_tok": int(np.median(L)),
             "p90_tok": int(np.percentile(L, 90)), "cut_16384": int((L >= 16384).sum()),
             "finish": {k: sum(r["finish"] == k for r in S) for k in ("stop", "length")},
             "stop_answer_tag": sum(r.get("stop_reason") == "</answer>" for r in S),
             "think_end": sum("</think>" in r["text"] for r in S),
             "answer_tag": sum("<answer>" in r["text"] for r in S),
             "im_end_in_response": sum((r.get("n_im_end") or 0) > 0 for r in S),
             "im_start_in_response": sum((r.get("n_im_start") or 0) > 0 for r in S),
             "tok_per_s": meta.get("tok_per_s"), "t_gen_s": meta.get("t_gen_s")}
        for task in ("ifeval", "rlzif"):
            rows = [G[(r["pid"], r["chunk"], r["i"])] for r in S if r["pid"].startswith(task)]
            Lt = [r["n_tok"] for r in S if r["pid"].startswith(task)]
            d[f"{task}_n"] = len(rows)
            d[f"{task}_mean_tok"] = round(float(np.mean(Lt))) if Lt else None
            if task == "ifeval":
                for g in ("strict", "loose", "closed", "t1"):
                    d[f"ifeval_{g}"] = round(float(np.mean([bool(r.get(g)) for r in rows])), 3) if rows else None
                d["ifeval_cont"] = sum(bool(r.get("cont")) for r in rows)
        out[job] = d
        print(job, json.dumps(d))
    return out


if __name__ == "__main__":
    main()
