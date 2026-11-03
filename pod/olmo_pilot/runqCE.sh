#!/usr/bin/env bash
# runqCE.sh <job> ...: phases C (confirmation) and E (sequential extension) from olmo_pilot/plan/*.txt (pid:n lists).
# Waits until no sampler runs on this pod; skips jobs with a .done marker, a JOB_START log line, or an empty plan file.
cd /workspace/nd-takehome; A=artifacts/olmo_pilot; L=$A/logs
RL=allenai/Olmo-3.1-7B-RL-Zero-Math; BASE=allenai/Olmo-3-1025-7B; PL=olmo_pilot/plan; FLAGS=$(cat olmo_pilot/sampler_flags.txt)
while pgrep -f 'olmo_pilot/[s]ample.py' > /dev/null; do sleep 30; done
for J in "$@"; do
  [ -f $A/meta/$J.done ] && continue
  grep -qs "JOB_START $J " $L/q_$J.log && { echo "skip $J (started before)"; continue; }
  X=""
  case $J in
    C_s2800) F=$PL/C_step_2800.txt; C="bash pod/olmo_pilot/job.sh C_s2800 step_2800 $RL step_2800 24 @$F 3001 1 8" ;;
    C_s0100) F=$PL/C_step_0100.txt; C="bash pod/olmo_pilot/job.sh C_s0100 step_0100 $RL step_0100 24 @$F 3002 1 8" ;;
    C_s0500) F=$PL/C_step_0500.txt; C="bash pod/olmo_pilot/job.sh C_s0500 step_0500 $RL step_0500 24 @$F 3003 1 8" ;;
    E1_base)  F=$PL/E_base.txt;  X="$FLAGS --seq_stop"; C="bash pod/olmo_pilot/job.sh E1_base base $BASE main 1 @$F 4001 1 16" ;;
    E1_s2800) F=$PL/E_s2800.txt; X="$FLAGS --seq_stop"; C="bash pod/olmo_pilot/job.sh E1_s2800 step_2800 $RL step_2800 1 @$F 4002 1 16" ;;
    *) echo "unknown job $J"; continue ;;
  esac
  [ -s $F ] && grep -q ':' $F || { echo "skip $J (no problems in $F)"; touch $A/meta/$J.done; continue; }
  echo "RUNQ start $J $(date -u +%FT%TZ)"
  if [ -n "$X" ]; then SAMPLE_EXTRA="$X" $C > $L/q_$J.log 2>&1; else $C > $L/q_$J.log 2>&1; fi
  echo "RUNQ end $J $(date -u +%FT%TZ) $(grep -o 'JOB_DONE.*' $L/q_$J.log)"
done
echo "QUEUE_DONE $(date -u +%FT%TZ)"
