#!/usr/bin/env bash
# J3 (pre-registered): guided (logical) reads, guided-tts settings (k 256, T 0.8, seed 1, batch 2,048, max_rej 10), of
# pend / r8 / r16 of seed S on textbook72 (dev58 + train14) + holdout250.  Resumable per checkpoint.
. pod/cd/env.sh
S=$1
SETS=data/gt/tb72_textbook_dev.jsonl,data/gt/tb72_textbook_train.jsonl,data/cd/h250_gt.jsonl
for M in pend r8 r16; do
  O=artifacts/cd/j3/s${S}_${M}_logical
  [ -s $O.json ] && { echo "skip $O"; continue; }
  echo "$(date -u +%FT%TZ) start $O"
  ND_ARM=j3_${M}_s${S} python3 guided_eval.py --ckpt $CK/s${S}_${M}.pt --arm logical --k 256 --seed 1 --batch 2048 --sets $SETS --out $O
  echo "$(date -u +%FT%TZ) end $O rc=$?"
done
