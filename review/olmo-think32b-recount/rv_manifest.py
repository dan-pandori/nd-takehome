"""Manifest check (reviewer): olmo32/problems.jsonl problem text and answer vs MathArena's datasets at the recorded
revisions."""
import json, os, sys
import pyarrow.parquet as pq
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
ours = [json.loads(l) for l in open(os.path.join(ROOT, "olmo32", "problems.jsonl"))]
ma = {}
for tag in ("aime2025", "aime2026"):
    t = pq.read_table(os.path.join(HERE, "out", "matharena", f"{tag}.parquet")).to_pylist()
    for r in t:
        ma[(tag, int(r["problem_idx"]))] = r
print("MathArena columns:", sorted(t[0].keys()), "rows:", len(ma))
bad_ans = []; bad_txt = []; n = 0
for r in ours:
    tag = r["set"]; idx = int(r["source"].split("problem_idx=")[1])
    m = ma.get((tag, idx)); n += 1
    if m is None:
        bad_ans.append((r["pid"], "missing")); continue
    if str(m["answer"]).strip() != str(r["answer"]).strip():
        bad_ans.append((r["pid"], m["answer"], r["answer"]))
    if m["problem"].strip() != r["problem"].strip():
        bad_txt.append(r["pid"])
print(f"{n} problems: answer mismatches {bad_ans}; text mismatches {len(bad_txt)} {bad_txt[:10]}")
print("pids:", sorted(set(r["set"] for r in ours)), "count per set:", {s: sum(r['set'] == s for r in ours) for s in ('aime2025', 'aime2026')})
