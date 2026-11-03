#!/usr/bin/env bash
# Stage 0, second half (after s0_base): step_2800 x 3 samples x 30 AIME 2023 problems (cut from 16 to keep Stage 0 within $3).
# The likelihood-scoring test and the weight distances move to the start of the main run.
cd /workspace/nd-takehome; A=artifacts/olmo_pilot
until [ -f $A/meta/s0_base.done ] || grep -q "JOB_DONE s0_base" $A/logs/stage0.log; do sleep 30; done
bash pod/olmo_pilot/job.sh s0_step2800 step_2800 allenai/Olmo-3.1-7B-RL-Zero-Math step_2800 3 @olmo_pilot/pilot_pids.txt 1001 0 3
echo "STAGE0_DONE $(date -u +%FT%TZ)"
