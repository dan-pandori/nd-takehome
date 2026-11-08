#!/usr/bin/env python3
"""Mechanical comparison of the answers written after RL's full genuine thinking (run olmo-transplant): how each
writer's answer relates to RL's own original answer on that trace (the stored answer the trace was labelled genuine
for). Reach prompts only; strict grades from graded/<job>.jsonl. Whitespace-collapsed text throughout.
Per writer: answers, strict successes, exact copies of RL's answer, answers that contain RL's answer verbatim (and how
many of those fail strict), answers > 1.5x RL's answer in words, median words of the writer's and of RL's answers.
Writes olmo_transplant/mechanism.md. Usage: mechanism.py"""
import collections
import csv
import gzip
import json
import re
import statistics as st

A = "artifacts/olmo_transplant"


def norm(s):
    return re.sub(r"\s+", " ", s).strip()


def main():
    T = {t["trace"]: t for t in csv.DictReader(open("olmo_transplant/traces.csv")) if t["kind"] == "rl" and t["set"] == "reach"}
    want = {(t["job"], t["pid"], int(t["chunk"]), int(t["i"])): k for k, t in T.items()}
    src = {}
    for jb in ("F_s2300_ifb", "C1_s2300_ifb", "C2_s2300_ifb"):
        for ln in gzip.open(f"{A}/src/{jb}.jsonl.gz", "rt"):
            r = json.loads(ln)
            k = (jb, r["pid"], r["chunk"], r["i"])
            if k in want:
                src[want[k]] = norm(r["text"].rsplit("</think>", 1)[1])
    out = ["# What the writers do with RL's full genuine thinking (reach, T1 vs T2; mechanism.py)", "",
           "| writer (cond) | answers | strict | exact copy of RL's answer | contains RL's answer | ... of which fail strict "
           "| > 1.5x RL's words | median words | RL's answer median words |", "|---|---|---|---|---|---|---|---|---|"]
    for job, cond in (("R_dpo", "T1"), ("R_s2300", "T2")):
        g = {(r["rid"], r["i"]): r for r in map(json.loads, open(f"{A}/graded/{job}.jsonl"))}
        c = collections.Counter()
        wds, srcw = [], []
        for ln in gzip.open(f"{A}/samples/{job}.jsonl.gz", "rt"):
            r = json.loads(ln)
            if r["cond"] != cond or r["trace"] not in src:
                continue
            a = norm(r["text"].rsplit("</think>", 1)[-1])
            s = src[r["trace"]]
            ok = g[(r["rid"], r["i"])]["strict"]
            c["n"] += 1
            c["strict"] += ok
            c["copy"] += a == s
            c["contains"] += s in a
            c["contains_fail"] += (s in a) and not ok
            c["longer"] += len(a.split()) > 1.5 * len(s.split())
            wds.append(len(a.split()))
            srcw.append(len(s.split()))
        out.append(f"| {job.split('_')[1]} ({cond}) | {c['n']} | {c['strict']} | {c['copy']} | {c['contains']} | "
                   f"{c['contains_fail']} | {c['longer']} | {st.median(wds):g} | {st.median(srcw):g} |")
    open("olmo_transplant/mechanism.md", "w").write("\n".join(out) + "\n")
    print("\n".join(out))


if __name__ == "__main__":
    main()
