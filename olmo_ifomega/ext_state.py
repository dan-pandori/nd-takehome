#!/usr/bin/env python3
"""State of a running (or finished) sequential job: per prompt, draws so far, successes by grade, positions, cuts.

Reads the job's samples file (complete rows only, so a file still being written is fine), grades rows not graded
before (cache: /tmp/ext_state_<job>.jsonl), and prints one line per prompt of the job's pid list.
Usage (on a pod, in /workspace/nd-takehome): ext_state.py <job>
"""
import gzip
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import grade  # noqa: E402

job = sys.argv[1]
probs = {r["pid"]: r for r in map(json.loads, open("olmo_ifomega/problems.jsonl"))}
want = {}
for x in open(f"olmo_ifomega/plan/{job}.pids").read().split():
    p, n = x.split(":")
    want[p] = int(n)
cache = Path(f"/tmp/ext_state_{job}.jsonl")
done = {}
if cache.exists():
    for ln in open(cache):
        r = json.loads(ln)
        done[(r["pid"], r["chunk"], r["i"])] = r
new = []
try:
    with gzip.open(f"artifacts/olmo_ifomega/samples/{job}.jsonl.gz", "rt") as f:
        for ln in f:
            r = json.loads(ln)
            k = (r["pid"], r["chunk"], r["i"])
            if k in done:
                continue
            g = grade.grade_one(probs[r["pid"]]["task"], r["text"], probs[r["pid"]])
            row = {"pid": r["pid"], "chunk": r["chunk"], "i": r["i"], "n_tok": r["n_tok"], "finish": r["finish"],
                   **{a: g[a] for a in ("strict", "omega", "rl", "doubly") if a in g}}
            done[k] = row
            new.append(row)
except (EOFError, json.JSONDecodeError, OSError):
    pass
with open(cache, "a") as f:
    for row in new:
        f.write(json.dumps(row) + "\n")
for p, n in want.items():
    rs = sorted((r for k, r in done.items() if k[0] == p), key=lambda r: (r["chunk"], r["i"]))
    grades = [a for a in ("strict", "omega", "rl", "doubly") if rs and a in rs[0]]
    s = " ".join(f"{a}={sum(r[a] for r in rs)}" for a in grades)
    prim = "strict" if "strict" in grades else "doubly"
    pos = [f"{r['chunk']}/{r['i']}" for r in rs if r.get(prim)]
    cut = sum(r["finish"] == "length" for r in rs)
    print(f"{p} draws={len(rs)}/{n} {s} cut={cut} {prim}_at={','.join(pos[:4])}")
