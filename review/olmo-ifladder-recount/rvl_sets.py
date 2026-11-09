"""My re-grade vs the executor's graded/*.jsonl, and per-cell automatic statistics.

Writes out/sets.{txt,json}: per job agreement (strict / loose), text == decode(ids), answers without '</think>',
answers with a second '</think>', length cuts; per (cell, pid): draws, strict, loose, strict successes in draw order
(my grade), cut-offs. Also out/strict_lists.json: {cell: {pid: [[chunk, i, ans_sha], ...]}} in draw order.
"""
import collections
import gzip
import json

from rvl_core import ART, CELL, JOBS, OUT, Tee, dump

P = Tee("sets.txt")
res = {"agree": {}, "cells": {}}
lists = {}
for job in JOBS:
    mine = [json.loads(l) for l in gzip.open(OUT / "regrade" / f"{job}.jsonl.gz", "rt")]
    ex = {}
    for l in open(ART / "graded" / f"{job}.jsonl"):
        r = json.loads(l)
        ex[(r["pid"], r["chunk"], r["i"])] = r
    c = collections.Counter()
    dis = []
    for r in mine:
        e = ex.get((r["pid"], r["chunk"], r["i"]))
        if e is None:
            c["missing in executor graded"] += 1
            continue
        c["strict_agree"] += r["strict"] == e["strict"]
        c["loose_agree"] += r["loose"] == e["loose"]
        if r["strict"] != e["strict"] or r["loose"] != e["loose"]:
            dis.append((r["pid"], r["chunk"], r["i"], r["strict"], e["strict"], r["loose"], e["loose"]))
        c["dec_ok"] += r["dec_ok"]
        c["no_close"] += r["ans_none"]
        c["two_close"] += r["n_close"] > 1
        c["cut"] += r["finish"] == "length"
        c["n_tok==n_ids"] += r["n_tok"] == r["n_ids"]
    c["rows"] = len(mine)
    c["executor_rows"] = len(ex)
    res["agree"][job] = dict(c)
    P(f"{job}: rows {len(mine)} (executor {len(ex)}); strict agree {c['strict_agree']}, loose agree "
      f"{c['loose_agree']}; text==decode {c['dec_ok']}; n_tok==len(ids) {c['n_tok==n_ids']}; no '</think>' "
      f"{c['no_close']}; >1 '</think>' {c['two_close']}; length cuts {c['cut']}; disagreements {dis[:5]}")
    cell = CELL[job]
    per = collections.defaultdict(lambda: {"n": 0, "strict": 0, "loose": 0, "cut": 0, "no_close": 0})
    sl = collections.defaultdict(list)
    for r in sorted(mine, key=lambda r: (r["pid"], r["chunk"], r["i"])):
        d = per[r["pid"]]
        d["n"] += 1
        d["strict"] += r["strict"]
        d["loose"] += r["loose"]
        d["cut"] += r["finish"] == "length"
        d["no_close"] += r["ans_none"]
        if r["strict"]:
            sl[r["pid"]].append([r["chunk"], r["i"], r["ans_sha"]])
    res["cells"][cell] = dict(per)
    lists[cell] = dict(sl)
dump(res, "sets.json")
dump(lists, "strict_lists.json")
# summary of strict successes per cell over the reach prompts
import csv
prompts = list(csv.DictReader(open(ART.parent.parent / "olmo_ifladder" / "prompts.csv")))
reach = [r["pid"] for r in prompts if r["set"] == "reach"]
for cell in ["R2", "R3", "R4", "S2", "S3", "S4", "LM", "LC"]:
    per = res["cells"][cell]
    pr = [p for p in reach if p in per]
    ns = [per[p]["strict"] for p in pr]
    P(f"cell {cell}: reach pids {len(pr)}; strict successes total {sum(ns)}; pids with >=1 strict {sum(x > 0 for x in ns)}, "
      f">=2 strict {sum(x >= 2 for x in ns)}; distinct strict answers {sum(len({s[2] for s in lists[cell].get(p, [])}) for p in pr)}")
