#!/usr/bin/env bash
# One read of a checkpoint on data/coe/read1054.jsonl (textbook72 scoring only + holdout250 + 732 tracked transfer theorems):
# k 256, T 0.8, 96 steps, 512 tokens per action, batch 512 (reads share the card with a ladder).
# Usage: bash pod/coe/read.sh <ckpt> <tag> <plain|guided> <sample-seed> [batch]
source pod/coe/env.sh
CK=$1; TAG=$2; KIND=$3; SS=$4; B=${5:-512}; OUT=artifacts/coe/eval/$TAG
[ -s "$CK" ] || { echo "READ FAILED no ckpt $CK"; exit 1; }
echo "=== read $TAG $KIND seed $SS batch $B $(date -u +%FT%TZ)"
if [ "$KIND" = plain ]; then
  if [ ! -s $OUT.json ]; then
    python3 state_eval.py --ckpt $CK --in data/coe/read1054.jsonl --k 256 --temperature 0.8 --seed $SS --batch $B \
      --max_action 512 --max_steps 96 --out $OUT.jsonl --summary $OUT.json || { echo "READ FAILED $TAG"; exit 1; }
    gzip -f $OUT.jsonl
  fi
else
  if [ ! -s $OUT.json ]; then
    python3 guided_eval.py --ckpt $CK --arm logical --sets data/coe/read1054.jsonl --k 256 --seed $SS --batch $B \
      --max_action 512 --max_steps 96 --max_rej 10 --out $OUT || { echo "READ FAILED $TAG"; exit 1; }
  fi
fi
up artifacts/coe/eval
echo "=== read done $TAG $(date -u +%FT%TZ)"
