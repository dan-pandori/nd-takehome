#!/usr/bin/env bash
# kal-6: read-outs of the three KAL-C models, each fetched from the bucket once kal-1 has saved it.
cd /workspace/nd-takehome; . pod/kal/env.sh
for s in 0 1 2; do
  C=ckpts/kalmar/stage1_kalC_s$s.pt
  until [ -s $C ]; do hf buckets cp $BK/kalmar-pretrain/$C $C > /dev/null 2>&1 || sleep 60; done
  EXT=0 bash pod/kal/eval_model.sh kalC_s$s $C kal 1024
done
