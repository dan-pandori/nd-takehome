#!/usr/bin/env python3
"""Candidates after phase F (pre-registration Part B), and the pid lists for phases C and E.

reach candidate : headline problem, >= 1 rl-correct sample from any RL checkpoint in F, 0 from the base in F
reverse candidate: headline problem, >= 1 rl-correct base sample in F, 0 from step_2800 in F
Phase C: each RL checkpoint that solved a reach candidate in F gets 24 fresh samples on it.
Phase E: base on reach candidates, step_2800 on reverse candidates, sequentially (one chunk of 16 in flight per
problem, stop at the first chunk with a correct sample) up to K samples in total per problem.

Usage: plan_next.py [K] [tag]  -> writes olmo_pilot/plan/{C_<model>,E_base,E_s2800}<tag>.txt (pid:n lists) and a
summary. F jobs not graded yet are left out; a later call with a tag (e.g. "b") plans only problems and confirmation
cells that no earlier batch planned, so candidates are processed in batches under the same rule.
"""
import csv
import json
import sys
from collections import defaultdict
from pathlib import Path

A = Path("artifacts/olmo_pilot/graded")
O = Path("olmo_pilot")
F = {"base": "F_base", "step_2800": "F_s2800", "step_0100": "F_s0100b", "step_0500": "F_s0500"}


def succ(job):
    s, n = defaultdict(int), defaultdict(int)
    for ln in open(A / f"{job}.jsonl"):
        r = json.loads(ln)
        n[r["pid"]] += 1
        s[r["pid"]] += bool(r["rl"])
    return s, n


def main():
    K = int(sys.argv[1]) if len(sys.argv) > 1 else 128
    excl = {r["pid"] for r in csv.DictReader(open(O / "exclusions.csv"))}
    head = [p for p in open(O / "eval_pids.txt").read().split() if p not in excl]
    S = {m: succ(j) for m, j in F.items() if (A / f"{j}.jsonl").exists()}
    rl = [m for m in F if m != "base" and m in S]
    tag = sys.argv[2] if len(sys.argv) > 2 else ""  # batch tag: a later batch plans only problems not planned before
    planned = set()
    for f in (O / "plan").glob("E_base*.txt"):
        if f.stem != f"E_base{tag}":
            planned |= {x.split(":")[0] for x in f.read_text().split()}
    reach = [p for p in head if S["base"][0][p] == 0 and any(S[m][0][p] > 0 for m in rl)]
    rev = [p for p in head if S["base"][0][p] > 0 and S["step_2800"][0][p] == 0]
    reach_new = [p for p in reach if p not in planned]
    out = O / "plan"
    out.mkdir(exist_ok=True)
    for m in rl:
        prev = set()
        for f in out.glob(f"C_{m}*.txt"):
            if f.stem != f"C_{m}{tag}":
                prev |= {x.split(":")[0] for x in f.read_text().split()}
        ps = [p for p in reach if S[m][0][p] > 0 and p not in prev]
        (out / f"C_{m}{tag}.txt").write_text(" ".join(f"{p}:24" for p in ps) + "\n")
    nb = {p: S["base"][1][p] for p in reach}
    nf = {p: S["step_2800"][1][p] for p in rev}
    (out / f"E_base{tag}.txt").write_text(" ".join(f"{p}:{K - nb[p]}" for p in reach_new if K > nb[p]) + "\n")
    if not tag:
        (out / "E_s2800.txt").write_text(" ".join(f"{p}:{K - nf[p]}" for p in rev if K > nf[p]) + "\n")
    summ = {"K": K, "tag": tag, "models_in_F": rl, "headline": len(head), "reach_candidates": reach,
            "reach_new_this_batch": reach_new, "reverse_candidates": rev,
            "confirm": {m: [p for p in reach if S[m][0][p] > 0] for m in rl}}
    json.dump(summ, open(out / f"summary{tag}.json", "w"), indent=1)
    print(json.dumps({k: (len(v) if isinstance(v, list) else v) for k, v in summ.items() if k != "confirm"}),
          {m: len(v) for m, v in summ["confirm"].items()})


if __name__ == "__main__":
    main()
