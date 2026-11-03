#!/usr/bin/env bash
# Pass 3 (K = 512) for the problems still unresolved at 256, then step_0100 on the random half (budget-gated rule) and
# its probe. Plans come from the graded pass-2 files on this pod.
cd /workspace/nd-takehome; A=artifacts/olmo_pilot
until grep -q QUEUE_DONE $A/logs/after_d2.log; do sleep 30; done
python3 - <<'PY'
import json, collections
def unresolved(job):
    n = collections.defaultdict(int); s = collections.defaultdict(int)
    for l in open(f"artifacts/olmo_pilot/graded/{job}.jsonl"):
        r = json.loads(l); n[r["pid"]] += 1; s[r["pid"]] += bool(r["rl"])
    return [p for p in sorted(n) if s[p] == 0 and n[p] >= 128]
b, f = unresolved("E2_base"), [p for p in unresolved("E2_s2800") if p == "aime2025_14"]
open("olmo_pilot/plan/E3_base.txt", "w").write(" ".join(f"{p}:256" for p in b) + "\n")
open("olmo_pilot/plan/E3_s2800.txt", "w").write(" ".join(f"{p}:256" for p in f) + "\n")
print("E3_base:", b, "E3_s2800:", f)
PY
bash pod/olmo_pilot/runqCE.sh E3_base E3_s2800 F_s0100h P_s0100
