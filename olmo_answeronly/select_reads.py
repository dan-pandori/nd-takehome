#!/usr/bin/env python3
"""Choose which strict successes the blinded readers read (run olmo-answeronly; pre-registration
preregistration/olmo-answeronly.md, Hand gate). olmo_transplant/select_reads.py with this run's paths, cells and caps
(reach A1-A4, L1-L3: 2 per (prompt, writer, cell); calibration A1-A4: 1), and two more label sources for identity
inheritance: olmo-transplant's final hand labels (olmo_transplant/handcheck.csv, same rules) and the olmo-ifladder
labels of the Leval_main traces used by L2 / L3. olmo_transplant/select_reads.py's description follows.


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
import os
import random
import re
import sys

A = "artifacts/olmo_answeronly"
SRC = "artifacts/olmo_answeronly/inputs"
SEED = 20261110
CAP = {c: 2 for c in ("A1", "A2", "A3", "A4", "L1", "L2", "L3")}
CAP_CAL = {c: 1 for c in ("A1", "A2", "A3", "A4")}


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
        for ln in gzip.open(f"{SRC}/{jb}.jsonl.gz", "rt"):
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
    for r in csv.DictReader(open("olmo_transplant/handcheck.csv")):  # olmo-transplant's final labels
        if r.get("final_label") and r.get("answer_norm"):
            lab[(r["pid"], r["answer_norm"])] = r["final_label"]
    if os.path.exists(f"{SRC}/Leval_main.jsonl.gz"):  # olmo-ifladder's labels of lora_main's own answers
        lv = {(r["job"], r["pid"], r["chunk"], r["i"]): r["final_label"]
              for r in csv.DictReader(open("olmo_ifladder/handcheck.csv")) if r["job"] == "Leval_main" and r["final_label"]}
        for ln in gzip.open(f"{SRC}/Leval_main.jsonl.gz", "rt"):
            r = json.loads(ln)
            k = ("Leval_main", r["pid"], str(r["chunk"]), str(r["i"]))
            if k in lv:
                lab[(r["pid"], answer(r["text"]))] = lv[k]
    try:
        for r in csv.DictReader(open("olmo_answeronly/handcheck.csv")):
            if r.get("final_label") and r.get("answer_norm"):
                lab[(r["pid"], r["answer_norm"])] = r["final_label"]
    except FileNotFoundError:
        pass
    return lab


def main():
    name, jobs = sys.argv[1], sys.argv[2:]
    if os.path.exists(f"{A}/hand/run/sel_{name}.csv"):
        raise SystemExit(f"round {name} already selected; use a new round name")
    os.makedirs(f"{A}/hand/run", exist_ok=True)
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
            key = f"{job}|{r['rid']}|{r['i']}"
            if not g[f"{r['rid']}|{r['i']}"]["strict"]:
                continue
            cells[(r["pid"], r["writer"], rcond(r))].append((key, answer("</think>" + r["text"])))
        for (pid, w, rc), items in sorted(cells.items()):
            st = sets.get(pid, "reach")
            base = rc  # A1..A4, L1..L3 as is
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
