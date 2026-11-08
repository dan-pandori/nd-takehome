#!/usr/bin/env python3
"""Interim candidates_fixed.csv while the base's fixed-phase jobs still run (from partial.py outputs).

Reach: the base has all 16 fixed-phase samples and 0 strict successes, some RL-Zero-IF checkpoint >= 1 / 8.
Reverse: the base has >= 1 strict success among its finished samples and main 0 / 8. Both are final once listed
(a prompt can only be added later, never removed). analyze.py rewrites the file from the graded files at the end.
Usage: interim_cands.py <partial.tsv> ...
"""
import csv
import json
import sys
from collections import defaultdict
from pathlib import Path

A, O = Path("artifacts/olmo_rlzero_if"), Path("olmo_rlzero_if")
probs = {r["pid"]: r for r in map(json.loads, open(O / "problems.jsonl"))}
excl = {r["pid"]: r["reason"] for r in csv.DictReader(open(O / "exclusions.csv")) if r["decision"] == "excluded"}
rl = defaultdict(lambda: defaultdict(int))
for job, m in (("F_s0100", "s0100"), ("F_s0500", "s0500"), ("F_main", "main")):
    for r in map(json.loads, open(A / "graded" / f"{job}.jsonl")):
        rl[r["pid"]][m] += int(r["strict"])
base = {}
for f in sys.argv[1:]:
    for ln in open(f):
        pid, n, s = ln.split()
        base[pid] = (int(n), int(s))
cand = []
for pid in sorted(probs):
    if pid not in base:
        continue
    n, s = base[pid]
    solvers = [m for m in ("s0100", "s0500", "main") if rl[pid][m] > 0]
    if n == 16 and s == 0 and solvers:
        cand.append({"task": probs[pid]["task"], "pid": pid, "kind": "reach", "grade": "strict",
                     "challengers": " ".join(solvers), "excluded": excl.get(pid, "")})
    if s > 0 and rl[pid]["main"] == 0:
        cand.append({"task": probs[pid]["task"], "pid": pid, "kind": "reverse", "grade": "strict",
                     "challengers": "base", "excluded": excl.get(pid, "")})
with open(O / "candidates_fixed.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=["task", "pid", "kind", "grade", "challengers", "excluded"], lineterminator="\n")
    w.writeheader()
    w.writerows(cand)
done = sum(1 for v in base.values() if v[0] == 16)
print(f"interim: base complete on {done} prompts; reach {sum(c['kind'] == 'reach' for c in cand)}, "
      f"reverse {sum(c['kind'] == 'reverse' for c in cand)}")
