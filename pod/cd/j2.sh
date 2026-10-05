#!/usr/bin/env bash
# J2 (pre-registered): large-k plain sampling of pend_S on its J2 theorems (k 16,384, 8 theorems per chunk, chunk seed
# 7000 + chunk) and calibration theorems (k 4,096, seed 7100); trajectory's read settings.  Resumable per chunk.
. pod/cd/env.sh
S=$1
for C in data/cd/j2/s${S}_c*.jsonl data/cd/j2/s${S}_cal.jsonl; do
  B=$(basename $C .jsonl); O=artifacts/cd/j2/${B}
  [ -s $O.json ] && { echo "skip $O"; continue; }
  if [ "${B##*_}" = cal ]; then K=4096; SEED=7100; else K=16384; SEED=$((7000 + 10#${B##*_c})); fi
  echo "$(date -u +%FT%TZ) start $B k $K seed $SEED"
  ND_ARM=j2_pend_s${S} python3 state_eval.py --ckpt $CK/s${S}_pend.pt --in $C --out $O.jsonl --summary $O.json --k $K \
    --temperature 0.8 --seed $SEED --batch 2048 --max_action 512 --max_steps 96 --lenfield n_lines
  echo "$(date -u +%FT%TZ) end $B rc=$?"
done
