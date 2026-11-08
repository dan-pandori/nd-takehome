"""How close is the written answer to the source trace's own final answer? (run olmo-transplant; post hoc)

For reach samples in T1 / T2 / P / B (rl traces): Jaccard similarity of word 3-gram sets between the
whitespace-collapsed answer and the trace's whitespace-collapsed final answer (olmo-ifomega stored text after
`</think>`); answers under 3 words compare word sets.
Classes: exact (= 1), near (>= 0.8), partial (0.5-0.8), own (< 0.5). Strict success and success share by class.
Output: out/copy.txt, out/copy.json
"""
import collections
import csv
import gzip
import json

from rvt_core import ART, OUT, SCR, Tee, answer_of, iter_gz, wsnorm

P = Tee("copy.txt")
tr = {r["trace"]: r for r in csv.DictReader(open(OUT / "traces_mine.csv"))}
need = {(m["job"], m["pid"], int(m["chunk"]), int(m["i"])): t for t, m in tr.items() if m["kind"] == "rl" and m["set"] == "reach"}
src = {}
for job in sorted({k[0] for k in need}):
    for r in iter_gz(SCR / "src" / f"{job}.jsonl.gz"):
        k = (job, r["pid"], r["chunk"], r["i"])
        if k in need:
            src[need[k]] = wsnorm(r["text"].split("</think>", 1)[1])


def grams(s):
    w = s.split()
    return {tuple(w[i:i + 3]) for i in range(len(w) - 2)} if len(w) >= 3 else {(x,) for x in w}


def jac(a, b):
    ga, gb = grams(a), grams(b)
    return len(ga & gb) / len(ga | gb) if ga | gb else 1.0


def cls(x):
    return "exact" if x == 1.0 else "near" if x >= 0.8 else "partial" if x >= 0.5 else "own"


res = {}
for job in ("R_dpo", "R_s2300"):
    g = {}
    with gzip.open(OUT / "regrade" / f"{job}.jsonl.gz", "rt") as f:
        for ln in f:
            x = json.loads(ln)
            g[x["key"]] = x["strict"]
    c = collections.defaultdict(lambda: collections.Counter())
    for r in iter_gz(ART / "samples" / f"{job}.jsonl.gz"):
        if r["trace"] not in src:
            continue
        cell = r["cond"] + (str(r["cut"]) if r["cond"] == "B" else "")
        a = wsnorm(answer_of("</think>" + r["text"]))
        x = 1.0 if a == src[r["trace"]] else min(0.999, jac(a, src[r["trace"]]))
        k = cls(x)
        st = g[f"{job}|{r['rid']}|{r['i']}"]
        c[cell][(k, "n")] += 1
        c[cell][(k, "strict")] += st
    for cell, v in sorted(c.items()):
        tot_s = sum(v[(k, "strict")] for k in ("exact", "near", "partial", "own"))
        parts = []
        for k in ("exact", "near", "partial", "own"):
            n, s = v[(k, "n")], v[(k, "strict")]
            parts.append(f"{k} {n} (strict {s}, rate {s / n if n else float('nan'):.2f})")
        P(f"{job} {cell:7s}: " + "; ".join(parts) + f"; strict successes {tot_s}, of them exact+near "
          f"{v[('exact', 'strict')] + v[('near', 'strict')]} ({100 * (v[('exact', 'strict')] + v[('near', 'strict')]) / max(1, tot_s):.0f} %)")
        res[f"{job}|{cell}"] = {f"{k}|{m}": v[(k, m)] for k in ("exact", "near", "partial", "own") for m in ("n", "strict")}
json.dump(res, open(OUT / "copy.json", "w"), indent=1)
