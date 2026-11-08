#!/usr/bin/env python3
"""Choose which strict successes the blinded readers read (pre-registration, Hand gate).

A run-condition is (writer, cond, cut) as sampled: T1, T2, T3, T4, T0, B<N>, P (and F<N> for fresh budget forcing).
Per (pid, run-condition), in a seeded order, up to CAP[cond] strict successes are read, counting distinct answers:
  - an answer (whitespace-collapsed) equal to an already-labelled answer on the same prompt inherits that label and is
    not read: the source trace's own answer (olmo_ifomega/handcheck.csv final_label, or this run's source reads for
    calibration), or any answer already read or already selected in this or an earlier round;
  - calibration B and P are strict only (not read).
Writes <out.csv> for handcheck.py prep (samples, graded, key, pid, rcond, set) and prints counts.
Usage: select_reads.py <round-name> <job> [<job> ...]   (jobs: graded/<job>.jsonl + samples/<job>.jsonl.gz)
"""
import collections
import csv
import gzip
import json
import random
import re
import sys

A = "artifacts/olmo_transplant"
SEED = 20261108
CAP = {"T1": 2, "T2": 2, "T3": 4, "T4": 4, "T0": 4, "B": 1, "P": 1, "F": 2}
CAP_CAL = {"T1": 1, "T2": 1, "T3": 1, "T4": 1, "T0": 1}


def norm(s):
    return re.sub(r"\s+", " ", s).strip()


def answer(text):
    return norm(text.rsplit("</think>", 1)[-1])


def rcond(r):
    if r["cond"] == "B":
        return f"B{r['cut']}"
    if r["cond"] == "F":
        return f"F{r['cut']}"
    return r["cond"]


def known_labels():
    """(pid, normalised answer) -> label, from every finished read (sources and this run's tables)."""
    lab = {}
    src = {}
    for jb in ("F_s2300_ifb", "C1_s2300_ifb", "C2_s2300_ifb"):
        for ln in gzip.open(f"{A}/src/{jb}.jsonl.gz", "rt"):
            r = json.loads(ln)
            src[(jb, r["pid"], r["chunk"], r["i"])] = r["text"]
    for r in csv.DictReader(open("olmo_ifomega/handcheck.csv")):
        k = (r["job"], r["pid"], int(r["chunk"]), int(r["i"]))
        if k in src and r["final_label"]:
            lab[(r["pid"], answer(src[k]))] = r["final_label"]
    try:
        for r in csv.DictReader(open("olmo_transplant/handcheck_src.csv")):
            job, pid, ch, i = r["key"].split("|")
            if r["final_label"]:
                lab[(pid, answer(src[(job, pid, int(ch), int(i))]))] = r["final_label"]
    except FileNotFoundError:
        pass
    try:
        for r in csv.DictReader(open("olmo_transplant/handcheck.csv")):
            if r.get("final_label") and r.get("answer_norm"):
                lab[(r["pid"], r["answer_norm"])] = r["final_label"]
    except FileNotFoundError:
        pass
    return lab


def main():
    name, jobs = sys.argv[1], sys.argv[2:]
    sets = {p["pid"]: p["set"] for p in csv.DictReader(open("olmo_transplant/prompts.csv"))}
    lab = known_labels()
    selected = set()
    for f in sorted(__import__("glob").glob(f"{A}/hand/run/sel_*.csv")):
        for r in csv.DictReader(open(f)):
            selected.add((r["pid"], r["answer_norm"]))
    out = []
    stats = collections.Counter()
    for job in jobs:
        g = {}
        for ln in open(f"{A}/graded/{job}.jsonl"):
            r = json.loads(ln)
            g[f"{r['rid']}|{r['i']}"] = r
        cells = collections.defaultdict(list)
        for ln in gzip.open(f"{A}/samples/{job}.jsonl.gz", "rt"):
            r = json.loads(ln)
            key = f"{r['rid']}|{r['i']}"
            if not g[key]["strict"]:
                continue
            cells[(r["pid"], r["writer"], rcond(r))].append((key, answer("</think>" + r["text"])))
        for (pid, w, rc), items in sorted(cells.items()):
            st = sets.get(pid, "reach")
            base = re.sub(r"\d+$", "", rc)
            cap = (CAP_CAL.get(base, 0) if st == "calib" else CAP[base])
            items.sort()
            random.Random(f"{SEED}|{name}|{pid}|{w}|{rc}").shuffle(items)
            n = 0
            for key, a in items:
                stats["strict"] += 1
                if (pid, a) in lab:
                    stats["inherit_known"] += 1
                    continue
                if (pid, a) in selected:
                    stats["inherit_selected"] += 1
                    continue
                if n >= cap:
                    stats["unread"] += 1
                    continue
                selected.add((pid, a))
                n += 1
                stats["read"] += 1
                out.append({"samples": f"{A}/samples/{job}.jsonl.gz", "graded": f"{A}/graded/{job}.jsonl", "key": key,
                            "pid": pid, "rcond": f"{w}:{rc}", "set": st, "answer_norm": a})
    with open(f"{A}/hand/run/sel_{name}.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["samples", "graded", "key", "pid", "rcond", "set", "answer_norm"])
        w.writeheader()
        w.writerows(out)
    print(name, dict(stats), "->", f"{A}/hand/run/sel_{name}.csv")


if __name__ == "__main__":
    main()
