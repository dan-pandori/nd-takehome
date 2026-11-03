#!/usr/bin/env bash
# Phase F (fixed budget, all 90 evaluation problems) then phase P (64 Dolci probe prompts x 1) for step_2800.
cd /workspace/nd-takehome; A=artifacts/olmo_pilot
[ -f $A/meta/F_s2800.done ] || bash pod/olmo_pilot/job.sh F_s2800 step_2800 allenai/Olmo-3.1-7B-RL-Zero-Math step_2800 8 @olmo_pilot/eval_pids.txt 2002 0 8
[ -f $A/meta/P_s2800.done ] || PROBLEMS=olmo_pilot/probe_prompts.jsonl bash pod/olmo_pilot/job.sh P_s2800 step_2800 allenai/Olmo-3.1-7B-RL-Zero-Math step_2800 1 - 5002 0 1
echo "QUEUE_DONE $(date -u +%FT%TZ)"
