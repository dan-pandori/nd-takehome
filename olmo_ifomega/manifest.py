#!/usr/bin/env python3
"""One row per evaluation prompt with its source, contamination flags and headline membership (olmo32's manifest.csv,
for this run). From problems.jsonl, contamination.csv (long format: pid x corpus) and exclusions.csv.
Columns: pid, task, family / source id, answer (OMEGA), {rl,dpo,sft}_max_raw / _max_content (8-gram containment of
the prompt in that training corpus; content = 8-grams with RL document frequency < 20), sft_best_source, excluded,
reason, run (the task's fixed phase ran: IFBench, IFEval and OMEGA test_out; test_in was cut).
Usage: manifest.py   -> olmo_ifomega/manifest.csv
"""
import csv
import json
from pathlib import Path

O = Path("olmo_ifomega")
RUN = {"ifbench", "ifeval", "omega_out"}


def main():
    probs = [json.loads(ln) for ln in open(O / "problems.jsonl")]
    con = {}
    for r in csv.DictReader(open(O / "contamination.csv")):
        con[(r["pid"], r["kind"])] = r
    excl = {r["pid"]: r for r in csv.DictReader(open(O / "exclusions.csv"))}
    rows = []
    for p in probs:
        row = {"pid": p["pid"], "task": p["task"], "family": p.get("family", ""),
               "source_id": p.get("omega_id", p.get("key", "")), "answer": p.get("answer", "")}
        for k in ("rl", "dpo", "sft"):
            c = con.get((p["pid"], k), {})
            row[f"{k}_max_raw"] = c.get("max_raw", "")
            row[f"{k}_max_content"] = c.get("max_content", "")
        row["sft_best_source"] = con.get((p["pid"], "sft"), {}).get("best_source", "")
        row["excluded"] = p["pid"] in excl
        row["reason"] = excl.get(p["pid"], {}).get("reason", "")
        row["run"] = p["task"] in RUN
        rows.append(row)
    with open(O / "manifest.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    by = {}
    for r in rows:
        by.setdefault(r["task"], [0, 0, 0])
        by[r["task"]][0] += 1
        by[r["task"]][1] += r["excluded"]
        by[r["task"]][2] += r["run"]
    print({t: dict(n=v[0], excluded=v[1], run=bool(v[2])) for t, v in by.items()})


if __name__ == "__main__":
    main()
