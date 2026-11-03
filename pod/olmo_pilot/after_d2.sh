#!/usr/bin/env bash
# After runqCE_d: pass 2. step_2800's extension covers the unresolved reverse candidate (aime2025_14, to 256) and, by the
# "same extension rule" symmetry, aime2025_22 (base solved it in its own extension; step_2800 had only its 8 F samples).
cd /workspace/nd-takehome; A=artifacts/olmo_pilot
until grep -q QUEUE_DONE $A/logs/runqCE_d.log; do sleep 30; done
echo "aime2025_14:128 aime2025_22:248" > olmo_pilot/plan/E2_s2800.txt
bash pod/olmo_pilot/runqCE.sh E2_base E2_s2800
