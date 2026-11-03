#!/usr/bin/env python3
"""Mean response length per checkpoint, from the graded job files, for the compute axis.

len_train = mean tokens per sample on the 64 probe prompts from the RL data (phase P job of that model);
len_eval  = mean tokens per sample over the model's phase-F samples on the 90 evaluation problems.
Writes olmo_pilot/lengths.csv (step, model, len_train, n_train, len_eval, n_eval) and runs compute_axis.py on it.
"""
import csv
import json
import subprocess
import sys
from collections import defaultdict
from pathlib import Path

A = Path("artifacts/olmo_pilot/graded")
O = Path("olmo_pilot")


def main():
    acc = defaultdict(lambda: {"P": [], "F": []})
    step = {}
    for j in csv.DictReader(open(O / "jobs.csv")):
        if j["phase"] not in ("probe", "fixed"):
            continue
        f = A / f"{j['job']}.jsonl"
        if not f.exists():
            continue
        step[j["model"]] = int(j["step"])
        key = "P" if j["phase"] == "probe" else "F"
        acc[j["model"]][key] += [json.loads(ln)["n_tok"] for ln in open(f)]
    rows = []
    for m in sorted(acc, key=lambda m: step[m]):
        p, f = acc[m]["P"], acc[m]["F"]
        if not p or not f:
            print(f"skip {m}: probe {len(p)} / eval {len(f)} samples")
            continue
        rows.append({"step": step[m], "model": m, "len_train": round(sum(p) / len(p), 1), "n_train": len(p),
                     "len_eval": round(sum(f) / len(f), 1), "n_eval": len(f)})
    with open(O / "lengths.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    for r in rows:
        print(r)
    subprocess.run([sys.executable, str(O / "compute_axis.py"), str(O / "lengths.csv"), str(O / "compute_axis.csv")],
                   check=True)


if __name__ == "__main__":
    main()
