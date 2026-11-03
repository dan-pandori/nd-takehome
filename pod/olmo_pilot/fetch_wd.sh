#!/usr/bin/env bash
# Shard 2 of the checkpoints used for the weight-distance check (which base revision RL-Zero started from).
cd /workspace/nd-takehome
for spec in "allenai/Olmo-3.1-7B-RL-Zero-Math step_0100 wd_step_0100" "allenai/Olmo-3.1-7B-RL-Zero-Math step_0200 wd_step_0200" \
            "allenai/Olmo-3-1025-7B stage3-step11000 wd_s3_11000" "allenai/Olmo-3-1025-7B stage2-step47684 wd_s2_47684"; do
  set -- $spec; bash pod/olmo_pilot/fetch.sh $1 $2 $3 model-00002-of-00003.safetensors
done
echo FETCH_WD_DONE
