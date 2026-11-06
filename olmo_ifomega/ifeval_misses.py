#!/usr/bin/env python3
"""How far dpo misses on IFEval's reach candidates (descriptive, from stored texts; not a pre-registered analysis).

For the 7 IFEval candidates dpo left unresolved at 256, measure each dpo response's distance from its one constraint
on the answer (text after the last </think>, stripped, as grade.py): letter_frequency -> count of the letter (case-
insensitive, as IFEval counts); english_capital -> lowercase letters in the answer; capital_word_frequency -> all-caps
words (a regex word census close to IFEval's nltk count). Responses without </think> have no answer and are counted as
such. near_miss (descriptive thresholds, chosen after seeing the medians; not pre-registered): letter count at most twice
the limit; lowercase letters under 10 % of the answer's letters; at most 15 all-caps words. s2300's fixed and
confirmation responses are measured the same way for contrast.
Usage: ifeval_misses.py   -> olmo_ifomega/ifeval_misses.csv (model, pid, constraint, limit, n, no_answer, pass,
                             median / p10 / p90 / min of the measured quantity, near_miss, median answer words)
"""
import csv
import gzip
import json
import re
import statistics
from pathlib import Path

A, O = Path("artifacts/olmo_ifomega"), Path("olmo_ifomega")
PIDS = ["ifeval_1130", "ifeval_1314", "ifeval_2247", "ifeval_2350", "ifeval_2447", "ifeval_2563", "ifeval_3478"]
JOBS = {"dpo": ["F_dpo_ife", "E1_dpo_ifev"], "s2300": ["F_s2300_ife", "C1_s2300_ifev"]}


def answer_of(text):
    return text.rsplit("</think>", 1)[1].strip() if "</think>" in text else None


def measure(prob, ans):
    """(what, limit, value, near_miss) for the prompt's one constraint."""
    ids, kw = prob["instruction_id_list"], prob["kwargs"]
    if ids[0] == "keywords:letter_frequency":
        k = kw[0]
        v = ans.lower().count(k["letter"].lower())
        return f"letter '{k['letter']}' count", f"< {k['let_frequency']}", v, v <= 2 * (k["let_frequency"] - 1)
    if ids[0] == "change_case:english_capital":
        v = sum(c.islower() for c in ans)
        return "lowercase letters", "0", v, v < 0.10 * max(1, sum(c.isalpha() for c in ans))
    if ids[0] == "change_case:capital_word_frequency":
        words = re.findall(r"\b[^\W\d_]+\b", ans)
        v = sum(w.isupper() for w in words)
        return "all-caps words", "1-10", v, v <= 15
    raise ValueError(ids)


def pct(xs, q):
    xs = sorted(xs)
    return xs[min(len(xs) - 1, int(q * len(xs)))]


def main():
    probs = {p["pid"]: p for p in map(json.loads, open(O / "problems.jsonl")) if p["pid"] in PIDS}
    grades = {}
    for jobs in JOBS.values():
        for j in jobs:
            for r in map(json.loads, open(A / "graded" / f"{j}.jsonl")):
                grades[(j, r["pid"], r["chunk"], r["i"])] = r["strict"]
    rows = []
    for model, jobs in JOBS.items():
        vals = {p: [] for p in PIDS}
        stats = {p: dict(n=0, no_answer=0, passed=0, near=0, words=[]) for p in PIDS}
        for j in jobs:
            with gzip.open(A / "samples" / f"{j}.jsonl.gz", "rt") as f:
                for r in map(json.loads, f):
                    if r["pid"] not in vals:
                        continue
                    s = stats[r["pid"]]
                    s["n"] += 1
                    s["passed"] += bool(grades.get((j, r["pid"], r["chunk"], r["i"])))
                    ans = answer_of(r["text"])
                    if ans is None:
                        s["no_answer"] += 1
                        continue
                    what, limit, v, near = measure(probs[r["pid"]], ans)
                    vals[r["pid"]].append(v)
                    s["near"] += bool(near) and not grades.get((j, r["pid"], r["chunk"], r["i"]))
                    s["words"].append(len(ans.split()))
        for p in PIDS:
            what, limit, _, _ = measure(probs[p], "")
            v, s = vals[p], stats[p]
            rows.append(dict(model=model, pid=p, measure=what, limit=limit, n=s["n"], no_answer=s["no_answer"],
                             passed=s["passed"], median=statistics.median(v) if v else "", p10=pct(v, 0.1) if v else "",
                             p90=pct(v, 0.9) if v else "", min=min(v) if v else "", near_miss_fail=s["near"],
                             median_words=statistics.median(s["words"]) if s["words"] else ""))
    with open(O / "ifeval_misses.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    for r in rows:
        print(r)


if __name__ == "__main__":
    main()
