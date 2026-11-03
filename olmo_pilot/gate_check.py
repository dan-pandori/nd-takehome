#!/usr/bin/env python3
"""Speculative-decoding gate (pre-registration Part B): adopt iff job-average throughput >= 1.25 x Stage 0 and the
95 % problem-bootstrap intervals of (gate - Stage 0) for pass@1 and for mean length both contain 0."""
import json
import sys
from collections import defaultdict

import numpy as np

A = "artifacts/olmo_pilot"


def per_problem(job):
    d = defaultdict(list)
    for ln in open(f"{A}/graded/{job}.jsonl"):
        r = json.loads(ln)
        d[r["pid"]].append((bool(r["rl"]), r["n_tok"]))
    return d


def main(gate="g_spec_base", ref="s0_base", ref_tps=557.2):
    ref_tps = float(ref_tps)
    g, s = per_problem(gate), per_problem(ref)
    pids = sorted(set(g) & set(s))
    p1 = np.array([[np.mean([x[0] for x in g[p]]), np.mean([x[0] for x in s[p]])] for p in pids])
    ln = np.array([[np.mean([x[1] for x in g[p]]), np.mean([x[1] for x in s[p]])] for p in pids])
    rng = np.random.default_rng(0)
    idx = rng.integers(0, len(pids), size=(10000, len(pids)))
    out = {}
    for name, M in (("pass1", p1), ("mean_tok", ln)):
        diff = M[idx, 0].mean(1) - M[idx, 1].mean(1)
        lo, hi = np.percentile(diff, [2.5, 97.5])
        out[name] = {"gate": round(float(M[:, 0].mean()), 4), "stage0": round(float(M[:, 1].mean()), 4),
                     "diff_lo95": round(float(lo), 4), "diff_hi95": round(float(hi), 4), "ok": bool(lo <= 0 <= hi)}
    tps = json.loads(open(f"{A}/meta/{gate}.json").readlines()[-1])["tok_per_s"]
    out["tok_per_s"] = {"gate": tps, "stage0": ref_tps, "ratio": round(tps / ref_tps, 3), "ok": tps >= 1.25 * ref_tps}
    out["adopt"] = all(v["ok"] for v in out.values() if isinstance(v, dict))
    print(json.dumps(out, indent=1))
    json.dump(out, open("olmo_pilot/gate_spec.json", "w"), indent=1)


if __name__ == "__main__":
    main(*sys.argv[1:])
