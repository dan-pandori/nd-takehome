#!/usr/bin/env bash
# weights.sh: Stage-0 weight checks (olmo_pilot/weight_dist.py, one shard = model-00002-of-00003.safetensors).
# (1) is `main` = step_1900? (2) did RL-Zero-IF start from base main (= stage3-step11921)? Waits for the jobs'
# full downloads of `base` and `main`, fetches shard 2 of the other revisions, writes meta/weight_dist.jsonl.
cd /workspace/nd-takehome; A=artifacts/olmo_rlzero_if; M=/workspace/models; SH=model-00002-of-00003.safetensors
F=pod/olmo_rlzero_if/fetch.sh
bash $F allenai/Olmo-3-7B-RL-Zero-IF step_1900 w_s1900 $SH
bash $F allenai/Olmo-3-7B-RL-Zero-IF step_1800 w_s1800 $SH
bash $F allenai/Olmo-3-7B-RL-Zero-IF step_100 w_s0100 $SH
bash $F allenai/Olmo-3-7B-RL-Zero-IF step_200 w_s0200 $SH
bash $F allenai/Olmo-3-1025-7B stage3-step11000 w_b11000 $SH
until [ -f $M/base/.complete ] && [ -f $M/main/.complete ]; do sleep 30; done
nice -n 10 python olmo_pilot/weight_dist.py main=$M/main/$SH s1900=$M/w_s1900/$SH s1800=$M/w_s1800/$SH \
  s0100=$M/w_s0100/$SH s0200=$M/w_s0200/$SH base=$M/base/$SH b11000=$M/w_b11000/$SH -- \
  main:s1900 main:s1800 s1900:s1800 s0100:base s0200:s0100 s0100:b11000 base:b11000 main:base | tee $A/meta/weight_dist.jsonl
echo "WEIGHTS_DONE $(date -u +%FT%TZ)"
