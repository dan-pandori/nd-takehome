#!/usr/bin/env bash
# J3 at cap 6 (pre-registered as "J3 cap 6 if the budget allows"): guided logical reads of best-cap6 pend / r8 / r16,
# guided-tts settings, textbook72 + holdout250.  Resumable.
. pod/cd/env.sh
S=$1
SETS=data/gt/tb72_textbook_dev.jsonl,data/gt/tb72_textbook_train.jsonl,data/cd/h250_gt.jsonl
for M in pend r8 r16; do
  O=artifacts/cd/j3/c6_s${S}_${M}_logical
  [ -s $O.json ] && { echo "skip $O"; continue; }
  echo "$(date -u +%FT%TZ) start $O"
  ND_ARM=j3c6_${M}_s${S} python3 guided_eval.py --ckpt $CK/c6_s${S}_${M}.pt --arm logical --k 256 --seed 1 --batch 2048 --sets $SETS --out $O
  echo "$(date -u +%FT%TZ) end $O rc=$?"
done
