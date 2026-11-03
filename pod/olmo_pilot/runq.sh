#!/usr/bin/env bash
# runq.sh <job> ...: run named jobs in order on this pod. Waits until no sampler is running here (so a queue can be
# replaced while its current job finishes), skips jobs whose .done marker or JOB_START log line exists.
cd /workspace/nd-takehome; A=artifacts/olmo_pilot; L=$A/logs
RL=allenai/Olmo-3.1-7B-RL-Zero-Math; BASE=allenai/Olmo-3-1025-7B; E=@olmo_pilot/eval_pids.txt; PP=olmo_pilot/probe_prompts.jsonl
while pgrep -f 'olmo_pilot/[s]ample.py' > /dev/null; do sleep 30; done
for J in "$@"; do
  [ -f $A/meta/$J.done ] && continue
  grep -qs "JOB_START $J " $L/q_$J.log && { echo "skip $J (started before)"; continue; }
  case $J in
    F_base)  C="bash pod/olmo_pilot/job.sh F_base base $BASE main 16 $E 2001 0 16" ;;
    F_s2800) C="bash pod/olmo_pilot/job.sh F_s2800 step_2800 $RL step_2800 8 $E 2002 0 8" ;;
    F_s0100) C="bash pod/olmo_pilot/job.sh F_s0100 step_0100 $RL step_0100 8 $E 2003 0 8" ;;
    F_s0500) C="bash pod/olmo_pilot/job.sh F_s0500 step_0500 $RL step_0500 8 $E 2004 0 8" ;;
    P_base)  C="env PROBLEMS=$PP bash pod/olmo_pilot/job.sh P_base base $BASE main 1 - 5001 0 1" ;;
    P_s2800) C="env PROBLEMS=$PP bash pod/olmo_pilot/job.sh P_s2800 step_2800 $RL step_2800 1 - 5002 0 1" ;;
    P_s0100) C="env PROBLEMS=$PP bash pod/olmo_pilot/job.sh P_s0100 step_0100 $RL step_0100 1 - 5003 0 1" ;;
    P_s0500) C="env PROBLEMS=$PP bash pod/olmo_pilot/job.sh P_s0500 step_0500 $RL step_0500 1 - 5004 0 1" ;;
    *) echo "unknown job $J"; continue ;;
  esac
  echo "RUNQ start $J $(date -u +%FT%TZ)"
  $C > $L/q_$J.log 2>&1
  echo "RUNQ end $J $(date -u +%FT%TZ) $(grep -o 'JOB_DONE.*' $L/q_$J.log)"
done
echo "QUEUE_DONE $(date -u +%FT%TZ)"
