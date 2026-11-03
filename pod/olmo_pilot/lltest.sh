#!/usr/bin/env bash
# Likelihood-scoring test on Stage-0 correct solutions (no sampling), then the weight-distance check (CPU).
cd /workspace/nd-takehome; A=artifacts/olmo_pilot; M=/workspace/models; S=model-00002-of-00003.safetensors
bash pod/olmo_pilot/fetch.sh allenai/Olmo-3-1025-7B main base
bash pod/olmo_pilot/fetch.sh allenai/Olmo-3.1-7B-RL-Zero-Math step_2800 step_2800
python olmo_pilot/ll_items.py --jobs s0_step2800,s0_base --tokenizer $M/base_tok --out $A/ll/s0_items.jsonl --cap 2 --max_per_job 24
for m in base step_2800; do
  python olmo_pilot/score_ll.py --model $M/$m --tokenizer $M/base_tok --name $m --items $A/ll/s0_items.jsonl --out $A/ll/s0_scored_$m.jsonl 2>&1 | tail -1
done
echo LLTEST_DONE
bash pod/olmo_pilot/fetch_wd.sh
python olmo_pilot/weight_dist.py base=$M/base/$S rl100=$M/wd_step_0100/$S rl200=$M/wd_step_0200/$S rl2800=$M/step_2800/$S \
  s3_11000=$M/wd_s3_11000/$S s2_47684=$M/wd_s2_47684/$S -- rl100:base rl200:rl100 rl2800:base rl100:s3_11000 base:s3_11000 rl100:s2_47684 base:s2_47684 > $A/meta/weight_dist.jsonl
cat $A/meta/weight_dist.jsonl; echo WD_DONE
