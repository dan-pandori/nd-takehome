#!/usr/bin/env bash
# Stage 0, second half (after s0_base): step_2800 x 2 samples x 30 AIME 2023 problems (cut from 16 to keep Stage 0 within $3); hard stop 03:31 UTC.
# The likelihood-scoring test and the weight distances move to the start of the main run.
cd /workspace/nd-takehome; A=artifacts/olmo_pilot
until [ -f $A/meta/s0_base.done ] || grep -q "JOB_DONE s0_base" $A/logs/stage0.log; do sleep 30; done
bash pod/olmo_pilot/job.sh s0_step2800 step_2800 allenai/Olmo-3.1-7B-RL-Zero-Math step_2800 2 @olmo_pilot/pilot_pids.txt 1001 0 2
echo "STAGE0_DONE $(date -u +%FT%TZ)"
