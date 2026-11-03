#!/usr/bin/env bash
# Stage 0 on one pod: base and step_2800 x 16 samples x 30 AIME 2023 problems; likelihood-scoring test; weight distances.
cd /workspace/nd-takehome; A=artifacts/olmo_pilot; L=$A/logs
until [ -f /workspace/models/base/.complete ]; do sleep 20; done
bash pod/olmo_pilot/fetch.sh allenai/Olmo-3.1-7B-RL-Zero-Math step_2800 step_2800 > $L/fetch_step_2800.log 2>&1 &
bash pod/olmo_pilot/job.sh s0_base base allenai/Olmo-3-1025-7B main 16 @olmo_pilot/pilot_pids.txt 1002
( for spec in "allenai/Olmo-3.1-7B-RL-Zero-Math step_0100 wd_step_0100" "allenai/Olmo-3.1-7B-RL-Zero-Math step_0200 wd_step_0200" \
              "allenai/Olmo-3-1025-7B stage3-step11000 wd_s3_11000" "allenai/Olmo-3-1025-7B stage2-step47684 wd_s2_47684"; do
    set -- $spec; bash pod/olmo_pilot/fetch.sh $1 $2 $3 model-00002-of-00003.safetensors; done ) > $L/fetch_wd.log 2>&1 &
wait
bash pod/olmo_pilot/job.sh s0_step2800 step_2800 allenai/Olmo-3.1-7B-RL-Zero-Math step_2800 16 @olmo_pilot/pilot_pids.txt 1001
python olmo_pilot/ll_items.py --jobs s0_step2800,s0_base --tokenizer /workspace/models/base --out $A/ll/s0_items.jsonl --cap 2 --max_per_job 24
for m in base step_2800; do
  python olmo_pilot/score_ll.py --model /workspace/models/$m --tokenizer /workspace/models/base --name $m --items $A/ll/s0_items.jsonl --out $A/ll/s0_scored_$m.jsonl 2>&1 | tail -1
done
M=/workspace/models; S=model-00002-of-00003.safetensors
python olmo_pilot/weight_dist.py base=$M/base/$S rl100=$M/wd_step_0100/$S rl200=$M/wd_step_0200/$S rl2800=$M/step_2800/$S \
  s3_11000=$M/wd_s3_11000/$S s2_47684=$M/wd_s2_47684/$S -- rl100:base rl200:rl100 rl2800:base rl100:s3_11000 base:s3_11000 rl100:s2_47684 base:s2_47684 > $A/meta/s0_weight_dist.jsonl
cat $A/meta/s0_weight_dist.jsonl
echo "STAGE0_DONE $(date -u +%FT%TZ)"
