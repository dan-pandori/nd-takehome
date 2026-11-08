#!/usr/bin/env python3
"""Per-prompt strict counts of a (possibly running) job from its samples file: complete rows only, cached grading.

Usage (on a pod, in /workspace/nd-takehome): partial.py <job> > <out.tsv>   (pid, rows, strict)
"""
import gzip
import json
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import grade  # noqa: E402

job = sys.argv[1]
probs = {r["pid"]: r for r in map(json.loads, open("olmo_rlzero_if/problems.jsonl"))}
cache = Path(f"/tmp/partial_{job}.jsonl")
done = {}
if cache.exists():
    for ln in open(cache):
        r = json.loads(ln)
        done[(r["pid"], r["chunk"], r["i"])] = r["strict"]
new = []
try:
    with gzip.open(f"artifacts/olmo_rlzero_if/samples/{job}.jsonl.gz", "rt") as f:
        for ln in f:
            r = json.loads(ln)
            k = (r["pid"], r["chunk"], r["i"])
            if k not in done:
                done[k] = grade.success(probs[r["pid"]]["task"], r["text"], probs[r["pid"]])
                new.append({"pid": k[0], "chunk": k[1], "i": k[2], "strict": done[k]})
except (EOFError, json.JSONDecodeError, OSError):
    pass
with open(cache, "a") as f:
    for r in new:
        f.write(json.dumps(r) + "\n")
agg = defaultdict(lambda: [0, 0])
for (pid, c, i), s in done.items():
    agg[pid][0] += 1
    agg[pid][1] += int(s)
for pid, (n, s) in sorted(agg.items()):
    print(f"{pid}\t{n}\t{s}")
