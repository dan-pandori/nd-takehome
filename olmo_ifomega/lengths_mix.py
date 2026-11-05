#!/usr/bin/env python3
"""Mean response length per checkpoint in RL's prompt mix, for compute_axis.py's middle estimate.

RL's prompt mix (Dolci-Think-RL-32B, olmo_ifomega/build_problems.py's census): 30 % maths, 29 % IF, 41 % code and
chat. Maths is represented by the checkpoint's mean fixed-phase response length on OMEGA test_out, IF by its mean on
IFBench (all 300 prompts), code and chat by the mean of the two. Only checkpoints measured on both tasks get a row
(dpo = step 0, s0750, s2300); compute_axis.py interpolates linearly in steps in between (step_0100 was cut on both).
Usage: lengths_mix.py   -> olmo_ifomega/lengths_mix.csv (step,mean_tok,omega_out_tok,ifbench_tok)
"""
import csv
import json
from collections import defaultdict
from pathlib import Path

A, O = Path("artifacts/olmo_ifomega"), Path("olmo_ifomega")
STEP = {"dpo": 0, "s0100": 100, "s0750": 750, "s2300": 2300}


def main():
    task = {r["pid"]: r["task"] for r in map(json.loads, open(O / "problems.jsonl"))}
    tok = defaultdict(list)
    for j in csv.DictReader(open(O / "jobs.csv")):
        f = A / "graded" / f"{j['job']}.jsonl"
        if j["phase"] != "fixed" or not f.exists():
            continue
        for r in map(json.loads, open(f)):
            if task.get(r["pid"]) in ("omega_out", "ifbench"):
                tok[(j["model"], task[r["pid"]])].append(r["n_tok"])
    rows = []
    for m, step in STEP.items():
        o, i = tok.get((m, "omega_out")), tok.get((m, "ifbench"))
        if not o or not i:
            continue
        mo, mi = sum(o) / len(o), sum(i) / len(i)
        rows.append({"step": step, "mean_tok": round(0.30 * mo + 0.29 * mi + 0.41 * (mo + mi) / 2),
                     "omega_out_tok": round(mo), "ifbench_tok": round(mi), "n_omega_out": len(o), "n_ifbench": len(i)})
    with open(O / "lengths_mix.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    for r in rows:
        print(r)


if __name__ == "__main__":
    main()
