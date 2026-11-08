#!/usr/bin/env python3
"""One row per evaluation prompt with its contamination flags (olmo_rlzero_if/manifest.csv).

Columns: pid, task, key, n_constraints, instruction ids, ifomega_excl (olmo-ifomega's Think-SFT/DPO/RL exclusion: the
218 = IFBench rows with it false), the RL-Zero-IF scan (contamination.csv: best raw / content containment and the RL
prompt keys), excluded (this run's decision, exclusions.csv) and the reason; headline = not excluded.
"""
import csv
import json
from pathlib import Path

O = Path("olmo_rlzero_if")
probs = [json.loads(l) for l in open(O / "problems.jsonl")]
con = {r["pid"]: r for r in csv.DictReader(open(O / "contamination.csv"))}
exc = {r["pid"]: r for r in csv.DictReader(open(O / "exclusions.csv"))}
rows = []
for p in probs:
    c, e = con[p["pid"]], exc.get(p["pid"], {})
    ids = p["instruction_id_list"]
    rows.append({"pid": p["pid"], "task": p["task"], "key": p.get("key", ""), "n_constraints": len(ids),
                 "instruction_ids": " ".join(ids), "ifomega_excl": p.get("ifomega_excl", False),
                 "rl_max_raw": c["rl_max_raw"], "rl_raw_doc": c["rl_raw_doc"], "rl_max_content": c["rl_max_content"],
                 "rl_content_doc": c["rl_content_doc"], "read": bool(e),
                 "excluded": e.get("decision") == "excluded", "reason": e.get("reason", ""),
                 "headline": e.get("decision") != "excluded"})
with open(O / "manifest.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0]))
    w.writeheader()
    w.writerows(rows)
print(f"manifest.csv {len(rows)} rows; excluded {sum(r['excluded'] for r in rows)}; headline IFBench "
      f"{sum(r['headline'] and r['task'] == 'ifbench' for r in rows)}, IFEval {sum(r['headline'] and r['task'] == 'ifeval' for r in rows)}; "
      f"s218 {sum((not r['ifomega_excl']) and r['task'] == 'ifbench' for r in rows)}")
