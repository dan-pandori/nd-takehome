#!/usr/bin/env bash
# Phase 0.2: per-attempt cost of the old full bases (trajectory pend s0-s2) on THIS pod's GPU class, alone on the GPU.
# Same plain read as the ladder's sampler (state_eval: T 0.8, 96 steps, 512 tokens/action) on the 322 (textbook72 + holdout250),
# k 256, at batch 2048 and 1024.  Usage: bash pod/coe/timing.sh <tag>
source pod/coe/env.sh
T=$1; mkdir -p artifacts/coe/timing
head -322 data/coe/read1054.jsonl > data/coe/r322.jsonl
for S in 0 1 2; do
  CK=ckpts/coe/old/stage1_best12_s${S}_b1200.pt
  [ -s $CK ] || { mkdir -p ckpts/coe/old; hf buckets cp $BK/trajectory/ckpts/tj/stage1_best12_s${S}_b1200.pt $CK >/dev/null 2>&1; }
  for B in 2048 1024 512; do
    O=artifacts/coe/timing/${T}_pend_s${S}_b$B
    [ -s $O.json ] || python3 state_eval.py --ckpt $CK --in data/coe/r322.jsonl --k 256 --temperature 0.8 --seed 0 \
      --batch $B --max_action 512 --max_steps 96 --summary $O.json > $O.log 2>&1
    python3 -c "import json;d=json.load(open('$O.json'));print('$T s$S b$B', d['solved'], round(d['wall_s'],1), 'ms/att', round(1000*d['wall_s']/(322*256),3), d['env'].get('peak_alloc_gb'))"
  done
done
nvidia-smi --query-gpu=name --format=csv,noheader
echo TIMING_DONE
