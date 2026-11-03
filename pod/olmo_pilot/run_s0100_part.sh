#!/usr/bin/env bash
# run_s0100_part.sh <job> <seed> <pidsfile> [then_probe]: phase F for step_0100 on a subset of problems (F_s0100 was split
# across two pods at ~07:50 UTC; the two jobs cover disjoint problems), optionally followed by the step_0100 probe.
cd /workspace/nd-takehome; A=artifacts/olmo_pilot; RL=allenai/Olmo-3.1-7B-RL-Zero-Math
while pgrep -f 'olmo_pilot/[s]ample.py' > /dev/null; do sleep 20; done
bash pod/olmo_pilot/job.sh $1 step_0100 $RL step_0100 8 @$3 $2 0 8 > $A/logs/q_$1_part.log 2>&1
grep -o 'JOB_DONE.*' $A/logs/q_$1_part.log
if [ -n "$4" ] && [ ! -f $A/meta/P_s0100.done ]; then
  PROBLEMS=olmo_pilot/probe_prompts.jsonl bash pod/olmo_pilot/job.sh P_s0100 step_0100 $RL step_0100 1 - 5003 0 1 > $A/logs/q_P_s0100.log 2>&1
fi
echo "PART_DONE $(date -u +%FT%TZ)"
