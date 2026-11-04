#!/usr/bin/env python3
"""Peek at a (possibly still-written) samples file: finished rows by task, mean / median tokens, cut share.
Usage: peek.py <samples.jsonl.gz> <problems.jsonl>"""
import gzip
import json
import sys
from collections import defaultdict

P = {r["pid"]: r["task"] for r in map(json.loads, open(sys.argv[2]))}
rows = []
try:
    with gzip.open(sys.argv[1], "rt") as f:
        for ln in f:
            rows.append(json.loads(ln))
except (EOFError, json.JSONDecodeError):
    pass
c = defaultdict(list)
for r in rows:
    c[P[r["pid"]]].append((r["n_tok"], r["finish"] == "length"))
for t, v in sorted(c.items()):
    toks = sorted(x for x, _ in v)
    print(f"{t:10s} n={len(v):4d} mean={sum(toks) / len(toks):8.0f} median={toks[len(toks) // 2]:6d} "
          f"max={toks[-1]:6d} cut={sum(y for _, y in v)}")
print("total finished", len(rows))
