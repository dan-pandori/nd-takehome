#!/usr/bin/env bash
# Weight-distance check (CPU): which base revision RL-Zero started from. Shard 2 of each checkpoint.
cd /workspace/nd-takehome; A=artifacts/olmo_pilot; M=/workspace/models; S=model-00002-of-00003.safetensors
cat artifacts/olmo_pilot/logs/fetch_wd.log | grep -E 'fetched|DONE'
nice -n 10 python olmo_pilot/weight_dist.py base=$M/base/$S rl100=$M/wd_step_0100/$S rl200=$M/wd_step_0200/$S rl2800=$M/step_2800/$S \
  s3_11000=$M/wd_s3_11000/$S s2_47684=$M/wd_s2_47684/$S -- rl100:base rl200:rl100 rl2800:base rl100:s3_11000 base:s3_11000 rl100:s2_47684 base:s2_47684 > $A/meta/weight_dist.jsonl
cat $A/meta/weight_dist.jsonl; echo WD_DONE
