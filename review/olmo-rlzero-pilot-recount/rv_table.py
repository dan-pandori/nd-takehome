#!/usr/bin/env python3
"""My own per-(model, problem) table from the raw rows.

Phase of each job is assigned here from its name (not from olmo_pilot/jobs.csv):
  F_<m>  fixed budget (phase F; F_s0100h = step_0100 on its half subset)   C_<m>  fresh confirmation
  E<k>_<m> sequential extension (pass k)      s0_*, g_spec_*  AIME 2023 pilot      P_* probe      F_s0100b void
Grades per sample: from my re-grade (out/regrade_<job>.jsonl: rl, main, my_int_ok) where the sample text exists;
F_base has no stored texts (graded rows only), so its rl/main/ansline are the executor's.
Writes out/table.json: {model|pid: {...}} and prints checks (key collisions, phase budgets).
"""
import json
from collections import defaultdict

import rv_core as R

MODEL = {"base": "base", "s2800": "step_2800", "s0500": "step_0500", "s0100h": "step_0100", "s0100b": "step_0100"}
JOBS = ["F_base", "F_s2800", "F_s0500", "F_s0100h", "C_s2800", "C_s0500", "E1_base", "E1_s2800", "E2_base",
        "E2_s2800", "E3_base", "E3_s2800"]


def phase(job):
    return {"F": "fixed", "C": "confirm", "E": "extension"}[job[0]]


def load_rows(job):
    f = R.OUT / f"regrade_{job}.jsonl"
    if f.exists():
        rows = [json.loads(l) for l in open(f)]
        for r in rows:
            r["src"] = "regrade"
        return rows
    g = R.graded(job)
    for r in g:
        r["src"] = "graded"
        r["my_int_ok"] = None
    return g


def build():
    probs = R.problems(with_probe=False)
    cells = defaultdict(list)
    keyset = defaultdict(set)
    collisions = []
    for job in JOBS:
        rows = load_rows(job)
        for r in rows:
            m = r["model"]
            k = (m, r["pid"], r["chunk"], r["i"])
            if k in keyset[m]:
                collisions.append((job, k))
            keyset[m].add(k)
            cells[(m, r["pid"])].append((r["chunk"], r["i"], phase(job), job, r))
    table = {}
    for (m, pid), ss in cells.items():
        ss.sort(key=lambda t: (t[0], t[1]))
        rec = {"model": m, "pid": pid, "set": probs[pid]["set"]}
        for ph in ("fixed", "confirm", "extension"):
            sub = [t for t in ss if t[2] == ph]
            rec[f"n_{ph}"] = len(sub)
            for gname in ("rl", "main"):
                rec[f"c_{ph}_{gname}"] = sum(bool(t[4][gname]) for t in sub)
        rec["attempts"] = len(ss)
        for gname in ("rl", "main"):
            ok = [bool(t[4][gname]) for t in ss]
            rec[f"succ_{gname}"] = sum(ok)
            rec[f"first_{gname}"] = ok.index(True) + 1 if any(ok) else None
        # format-robust integer read-out: mine where texts exist, else the executor's ansline (F_base)
        fr = []
        for t in ss:
            r = t[4]
            fr.append(bool(r["my_int_ok"]) if r.get("my_int_ok") is not None else bool(r.get("ansline")))
        rec["succ_int"] = sum(fr)
        rec["first_int"] = fr.index(True) + 1 if any(fr) else None
        rec["n_int_from_executor"] = sum(1 for t in ss if t[4].get("my_int_ok") is None)
        rec["mean_tok"] = sum(t[4]["n_tok"] for t in ss) / len(ss)
        rec["mean_tok_fixed"] = (sum(t[4]["n_tok"] for t in ss if t[2] == "fixed") / rec["n_fixed"]) if rec["n_fixed"] else None
        rec["cut_fixed"] = sum(t[4]["finish"] == "length" for t in ss if t[2] == "fixed")
        rec["jobs"] = sorted({t[3] for t in ss})
        rec["chunks"] = sorted({(t[3], t[0]) for t in ss})
        table[f"{m}|{pid}"] = rec
    return table, collisions


def main():
    table, coll = build()
    for v in table.values():
        v["chunks"] = [list(x) for x in v["chunks"]]
    json.dump(table, open(R.OUT / "table.json", "w"), indent=0)
    print("cells:", len(table), "key collisions:", len(coll), coll[:5])
    by_m = defaultdict(lambda: defaultdict(int))
    for v in table.values():
        by_m[v["model"]]["cells"] += 1
        by_m[v["model"]]["fixed"] += v["n_fixed"]
        by_m[v["model"]]["confirm"] += v["n_confirm"]
        by_m[v["model"]]["extension"] += v["n_extension"]
    for m, d in by_m.items():
        print(m, dict(d))


if __name__ == "__main__":
    main()
