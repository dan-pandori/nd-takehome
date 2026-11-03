#!/usr/bin/env bash
# After pass 3: phase L (likelihood scoring, required) first, then the budget-gated step_0100 half and its probe.
cd /workspace/nd-takehome; A=artifacts/olmo_pilot
while pgrep -f 'olmo_pilot/[s]ample.py' > /dev/null; do sleep 30; done
bash pod/olmo_pilot/llrun.sh > $A/logs/llrun.log 2>&1
grep -E 'tok_per_s|LL_DONE' $A/logs/llrun.log
bash pod/olmo_pilot/runqCE.sh F_s0100h P_s0100
