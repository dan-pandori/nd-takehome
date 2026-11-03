#!/usr/bin/env bash
# After runqCE_d (C_s2800, E1_s2800, C_s0500): plan step_2800's pass-2 reverse extension from E1_s2800, then run pass 2.
cd /workspace/nd-takehome; A=artifacts/olmo_pilot
until grep -q QUEUE_DONE $A/logs/runqCE_d.log; do sleep 30; done
python3 - <<'PY'
import json, collections
d = collections.defaultdict(int); n = collections.defaultdict(int)
for l in open("artifacts/olmo_pilot/graded/E1_s2800.jsonl"):
    r = json.loads(l); n[r["pid"]] += 1; d[r["pid"]] += bool(r["rl"])
open("olmo_pilot/plan/E2_s2800.txt", "w").write(" ".join(f"{p}:128" for p in sorted(n) if d[p] == 0) + "\n")
print("E2_s2800:", open("olmo_pilot/plan/E2_s2800.txt").read().strip())
PY
bash pod/olmo_pilot/runqCE.sh E2_base E2_s2800
