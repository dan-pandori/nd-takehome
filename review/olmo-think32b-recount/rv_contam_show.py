"""Show the best 8-gram-matching RL prompts (full text) for the candidate problems (reviewer)."""
import glob, json, os, sys
import pyarrow.parquet as pq
HERE = os.path.dirname(os.path.abspath(__file__))
rows = {r["pid"]: r for r in json.load(open(os.path.join(HERE, "out", "contam_rl.json")))["rows"]}
want = {rows[p]["c8_doc"]: p for p in ("aime2025_28", "aime2026_14")}
for f in sorted(glob.glob(sys.argv[1] + "/*.parquet")):
    t = pq.read_table(f, columns=["prompt", "ground_truth", "custom_id"]).to_pylist()
    for r in t:
        if r["custom_id"] in want:
            print("==", want[r["custom_id"]], "c8", rows[want[r["custom_id"]]]["c8"], r["custom_id"], "gt", r["ground_truth"])
            print(r["prompt"][:1500]); print()
