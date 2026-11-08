"""Cells in draw order from my re-grade (out/regrade/*.jsonl), and everything that follows mechanically from them.

Draw order per (model, pid): job order (fixed F_* < C1_* / E1 < E2 < E3 < E4; diagnostics apart), then chunk, then i
(chunk numbers restart at 0 in every job; the sequential jobs' stopping counts run over chunks in index order).
Writes out/cells.json: {model: {pid: [[job, chunk, i, strict, loose, n_tok, finish, t1, think_end], ...]}}."""
import json
import os
from collections import defaultdict

import rv_core as C

JOB_ORDER = {"F": 0, "C1": 1, "E1": 1, "E2": 2, "E3": 3, "E4": 4, "D": 9, "s0": -1}
EXCL = {"ifbench_196", "ifbench_228", "ifbench_285"}       # my rv_contam: content >= 0.5 (the only RULE-EXCLUDE rows)


def job_rank(job):
    return JOB_ORDER[job.split("_")[0]]


def build():
    cells = defaultdict(lambda: defaultdict(list))
    for fn in sorted(os.listdir(os.path.join(C.OUT, "regrade"))):
        if not fn.endswith(".jsonl"):
            continue
        job = fn[:-6]
        if job.startswith("s0_") or job == "F_math_void":
            continue
        for r in map(json.loads, open(os.path.join(C.OUT, "regrade", fn))):
            if r["task"] not in ("ifbench", "ifeval"):
                continue
            # the base-tokenizer diagnostic's rows carry model "base" (rev main): keep them apart
            m = "base_btok" if job.startswith("D_base_btok") else r["model"]
            cells[m][r["pid"]].append([job, r["chunk"], r["i"], r["strict"], r["loose"], r["n_tok"],
                                                r["finish"], r.get("t1"), r["think_end"]])
    for m in cells:
        for p in cells[m]:
            cells[m][p].sort(key=lambda x: (job_rank(x[0]), x[0], x[1], x[2]))
    return cells


def sets(P):
    ifb = sorted(p for p, r in P.items() if r["task"] == "ifbench")
    return {"ifbench_h297": [p for p in ifb if p not in EXCL], "ifbench_all300": ifb,
            "ifbench_s218": [p for p in ifb if not P[p]["ifomega_excl"]],
            "ifeval_all150": sorted(p for p, r in P.items() if r["task"] == "ifeval")}


if __name__ == "__main__":
    P = C.load_problems()
    cells = build()
    json.dump(cells, open(os.path.join(C.OUT, "cells.json"), "w"))
    for m in sorted(cells):
        n = sum(len(v) for v in cells[m].values())
        print(m, len(cells[m]), "pids", n, "draws")
