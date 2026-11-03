#!/usr/bin/env bash
# Phase F (fixed budget, all 90 evaluation problems) then phase P (64 Dolci probe prompts x 1) for step_0100.
cd /workspace/nd-takehome; A=artifacts/olmo_pilot
[ -f $A/meta/F_s0100.done ] || bash pod/olmo_pilot/job.sh F_s0100 step_0100 allenai/Olmo-3.1-7B-RL-Zero-Math step_0100 8 @olmo_pilot/eval_pids.txt 2003 0 8
[ -f $A/meta/P_s0100.done ] || PROBLEMS=olmo_pilot/probe_prompts.jsonl bash pod/olmo_pilot/job.sh P_s0100 step_0100 allenai/Olmo-3.1-7B-RL-Zero-Math step_0100 1 - 5003 0 1
echo "QUEUE_DONE $(date -u +%FT%TZ)"
