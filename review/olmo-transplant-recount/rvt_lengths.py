"""Answer lengths (words) by writer and cell on reach, and the source traces' answer lengths (post hoc description).
Output: out/lengths.txt"""
import collections
import csv
import gzip
import json
import statistics

from rvt_core import ART, OUT, SCR, Tee, answer_of, iter_gz

P = Tee("lengths.txt")
tr = {r["trace"]: r for r in csv.DictReader(open(OUT / "traces_mine.csv"))}
need = {(m["job"], m["pid"], int(m["chunk"]), int(m["i"])): t for t, m in tr.items() if m["set"] == "reach"}
srcw = {}
for job in sorted({k[0] for k in need}):
    for r in iter_gz(SCR / "src" / f"{job}.jsonl.gz"):
        k = (job, r["pid"], r["chunk"], r["i"])
        if k in need:
            srcw[need[k]] = len(r["text"].split("</think>", 1)[1].split())
for kind in ("rl", "dpo"):
    w = sorted(v for t, v in srcw.items() if tr[t]["kind"] == kind)
    P(f"source {kind} traces (reach): answer words median {statistics.median(w)}, q90 {w[int(0.9 * (len(w) - 1))]}, n {len(w)}")
for job in ("R_dpo", "R_s2300"):
    g = {}
    with gzip.open(OUT / "regrade" / f"{job}.jsonl.gz", "rt") as f:
        for ln in f:
            x = json.loads(ln)
            g[x["key"]] = x
    c = collections.defaultdict(list)
    fails = collections.defaultdict(collections.Counter)
    for r in iter_gz(ART / "samples" / f"{job}.jsonl.gz"):
        cell = r["cond"] + (str(r["cut"]) if r["cond"] == "B" else "")
        x = g[f"{job}|{r['rid']}|{r['i']}"]
        c[cell].append((x["words"], x["strict"], r["n_tok"]))
    for cell, v in sorted(c.items()):
        ws = sorted(a for a, _, _ in v)
        wss = sorted(a for a, s, _ in v if s)
        toks = sorted(t for _, _, t in v)
        P(f"{job} {cell:7s} n {len(v):5d}: answer words median {statistics.median(ws):.0f} (q90 {ws[int(0.9 * (len(ws) - 1))]}); "
          f"strict successes' median {statistics.median(wss) if wss else float('nan'):.0f}; generated tokens median "
          f"{statistics.median(toks):.0f}")
