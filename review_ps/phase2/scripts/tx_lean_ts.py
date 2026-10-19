#!/usr/bin/env python3
"""Phase-2 sub-audit: run the project's lean_check judge (its PRELUDE / allowlist / node counter, via the internal _run,
NOT check(), which would write a compute-registry row) on the 30 Lean texts of artifacts/ps/examples.json exactly as shown
(`example` -> `theorem t`).  Reports ok + inference-node count per example vs the term size EXAMPLES.md prints and the
per-rule formula (labels ts).  Lean 4.34.0 binary; temp files under /tmp only.  Run with python3 -B (no __pycache__)."""
import json
import os
import sys
import tempfile

os.environ["LEAN"] = os.path.expanduser("~/.elan/toolchains/leanprover--lean4---v4.34.0/bin/lean")
sys.path.insert(0, "/home/dan/work/proof-strategies")
import lean_check  # noqa: E402

E = json.load(open("/home/dan/work/proof-strategies/artifacts/ps/examples.json"))["examples"]
srcs = [e["lean"].replace("example ", "theorem t ", 1) for e in E]
wd = tempfile.mkdtemp(prefix="tx_leants_", dir="/tmp")
res, cpu = lean_check._run(srcs, wd, "tx")
os.rmdir(wd)
out = []
for n, (e, r) in enumerate(zip(E, res)):
    row = {"n": n, "strategy": e["strategy"], "role": e["role"].split(" (")[0], "index": e["index"], "ok": r["ok"],
           "lean_check_size": r["size"], "shown_term_size": e["term_size_lean"], "formula_ts": e["labels"]["ts"],
           "reason": r["reason"]}
    out.append(row)
    print(json.dumps(row))
print("accepted:", sum(r["ok"] for r in out), "/", len(out),
      "| size == shown:", sum(r["lean_check_size"] == r["shown_term_size"] for r in out),
      "| size == formula:", sum(r["lean_check_size"] == r["formula_ts"] for r in out), "| lean s:", round(cpu, 1))
json.dump(out, open("/home/dan/review/proof-strategies/phase2/scripts/tx_lean_ts.out.json", "w"), indent=1)
