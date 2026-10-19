#!/usr/bin/env python3
"""Phase-2 sub-audit (TAXONOMY §6 'a 587-proof renderer test'): the artifact's producer is not committed, so re-run an
equivalent test with my own sample: lean_render.render on 300 random K12 proofs (seed 7), all 187 Charles reference
proofs (private: never printed) and 100 random textbook-schema search proofs (seed 7), judged by lean_check's own
prelude/allowlist via _run (not check(): no registry row).  Counts only.  python3 -B."""
import gzip, json, os, random, sys, tempfile
os.environ["LEAN"] = os.path.expanduser("~/.elan/toolchains/leanprover--lean4---v4.34.0/bin/lean")
sys.path.insert(0, "/home/dan/work/proof-strategies"); sys.path.insert(0, "/home/dan/work/proof-strategies/proof_strategies")
import lean_check  # noqa: E402
from lean_render import render  # noqa: E402
rng = random.Random(7)
want = set(rng.sample(range(155000), 300))
k12 = []
with gzip.open("/home/dan/review/proof-strategies/data/ps/in/train_k12.jsonl.gz", "rt") as f:
    for n, l in enumerate(f):
        if n in want:
            r = json.loads(l); k12.append((r["prompt"], r["proof"]))
ch = [json.loads(l) for l in open("/home/dan/work/proof-strategies/data/ps/in/charles/charles_base_full.jsonl")]
ch = [(r["prompt"], r["reference_proof"]) for r in ch]
ts = [json.loads(l) for l in open("/home/dan/work/proof-strategies/data/ps/search/tb_schema.checked.jsonl")]
ts = [(r["prompt"], r["proof"]) for r in random.Random(7).sample(ts, 100)]
for tag, rows in (("k12", k12), ("charles_base", ch), ("tb_schema", ts)):
    srcs, fail_render = [], 0
    for p, pr in rows:
        try:
            srcs.append(render(p, pr))
        except Exception:
            fail_render += 1
    wd = tempfile.mkdtemp(prefix="tx_r587_", dir="/tmp")
    res, _ = lean_check._run(srcs, wd, tag)
    os.rmdir(wd)
    print(tag, "n", len(rows), "| render errors", fail_render, "| lean_check accepted", sum(r["ok"] for r in res), "/", len(srcs))
