#!/usr/bin/env bash
# Phase F (fixed budget, all 90 evaluation problems) then phase P (64 Dolci probe prompts x 1) for base.
cd /workspace/nd-takehome; A=artifacts/olmo_pilot
[ -f $A/meta/F_base.done ] || bash pod/olmo_pilot/job.sh F_base base allenai/Olmo-3-1025-7B main 16 @olmo_pilot/eval_pids.txt 2001 0 16
[ -f $A/meta/P_base.done ] || PROBLEMS=olmo_pilot/probe_prompts.jsonl bash pod/olmo_pilot/job.sh P_base base allenai/Olmo-3-1025-7B main 1 - 5001 0 1
echo "QUEUE_DONE $(date -u +%FT%TZ)"
