"""Per model x prompt cell table from my re-graded rows (out/regrade/*.jsonl), in draw order.

Draw order of one (model, pid): the fixed-phase job F_* (chunk, i), then that model's defender jobs E1 < E2 < E3, or its
challenger jobs C1 < C2 < C3 (chunk, i). A model is defender or challenger on a prompt, never both (asserted).
Output: out/cells.csv (one row per model x pid) and out/draws.json (per cell: per-grade success flags in draw order,
with the job of each draw) used by rv_stats.py / rv_ext.py / rv_hand_items.py."""
import csv
import json
import os
import re
from collections import defaultdict

import rv_core as C

GRADES = {"ifbench": ("strict", "loose", "rlview"), "ifeval": ("strict", "loose", "rlview"),
          "omega_out": ("omega", "rl", "doubly", "own"), "omega_in": ("omega", "rl", "doubly", "own")}


def job_kind(job):
    m = re.match(r"^(F|E|C)(\d?)_", job)
    if job.startswith("s0_"):
        return ("S", 0)
    return (m.group(1), int(m.group(2) or 0))


def build():
    P = C.load_problems()
    draws = defaultdict(list)  # (model, pid) -> list of (kind, stage, job, chunk, i, row)
    for job in C.jobs():
        if job.startswith("s0_"):
            continue
        k, s = job_kind(job)
        for r in C.load_regrade(job):
            if r["task"] in ("omega_out", "omega_in"):
                r["doubly"] = bool(r["omega"] and r["rl"])
            draws[(r["model"], r["pid"])].append((k, s, job, r["chunk"], r["i"], r))
    cells = {}
    for (m, pid), lst in draws.items():
        kinds = {x[0] for x in lst}
        assert not ({"E", "C"} <= kinds), (m, pid, kinds)
        order = {"F": 0, "E": 1, "C": 1}
        lst.sort(key=lambda x: (order[x[0]], x[1], x[2], x[3], x[4]))
        keys = [(x[2], x[3], x[4]) for x in lst]
        assert len(set(keys)) == len(keys), ("duplicate draw", m, pid)
        task = P[pid]["task"]
        cells[(m, pid)] = {
            "model": m, "pid": pid, "task": task,
            "jobs": [x[2] for x in lst], "role": ("E" if "E" in kinds else "C" if "C" in kinds else "F"),
            "fixed": [x[0] == "F" for x in lst],
            "n_tok": [x[5]["n_tok"] for x in lst], "finish": [x[5]["finish"] for x in lst],
            "think_end": [x[5]["think_end"] for x in lst],
            "g": {g: [bool(x[5][g]) for x in lst] for g in GRADES[task]},
            "per": [x[5].get("per") for x in lst] if task in ("ifbench", "ifeval") else None,
            "ans": [x[5].get("omega_ans") for x in lst] if task.startswith("omega") else None,
            "key": [list(k) for k in keys],
        }
    return cells


def first_k(flags, k):
    """1-based draw indices of the first k successes."""
    out = [j + 1 for j, f in enumerate(flags) if f][:k]
    return out + [None] * (k - len(out))


def main():
    cells = build()
    os.makedirs(C.OUT, exist_ok=True)
    with open(os.path.join(C.BIG, "draws.json"), "w") as f:
        json.dump({f"{m}|{p}": v for (m, p), v in cells.items()}, f)
    cols = ["model", "pid", "task", "role", "n_fixed", "n_all", "n_cap256", "cut_all", "think_end_all", "mean_tok"]
    gcols = []
    for g in ("strict", "loose", "rlview", "omega", "rl", "doubly", "own"):
        gcols += [f"{g}_fixed", f"{g}_all256", f"{g}_first", f"{g}_second"]
    with open(os.path.join(C.OUT, "cells.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(cols + gcols)
        for (m, p), c in sorted(cells.items(), key=lambda t: (t[1]["task"], t[0][1], t[0][0])):
            nf = sum(c["fixed"])
            n = len(c["fixed"])
            row = [m, p, c["task"], c["role"], nf, n, min(n, 256), sum(x == "length" for x in c["finish"]),
                   sum(c["think_end"]), round(sum(c["n_tok"]) / n)]
            for g in ("strict", "loose", "rlview", "omega", "rl", "doubly", "own"):
                if g not in c["g"]:
                    row += ["", "", "", ""]
                    continue
                fl = c["g"][g]
                a, b = first_k(fl[:256], 2)
                row += [sum(fl[:nf]), sum(fl[:256]), a, b]
            w.writerow(row)
    print("cells:", len(cells))


if __name__ == "__main__":
    main()
