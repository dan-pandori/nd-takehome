#!/usr/bin/env bash
# Re-run any J3 / J3-cap-6 guided read whose output is missing (an OOM at batch 2,048) at batch 1,024; same checkpoint,
# arm, k, T, seed and sets (a re-draw at a smaller batch, logged in log.md).  Usage: j3fix.sh "c6_s1_r8 s0_r16 ..."
. pod/cd/env.sh
SETS=data/gt/tb72_textbook_dev.jsonl,data/gt/tb72_textbook_train.jsonl,data/cd/h250_gt.jsonl
for T in $(echo $1 | tr ',' ' '); do
  O=artifacts/cd/j3/${T}_logical
  [ -s $O.json ] && { echo "skip $O"; continue; }
  echo "$(date -u +%FT%TZ) start $O (batch 1024)"
  ND_ARM=j3fix_${T} python3 guided_eval.py --ckpt $CK/${T}.pt --arm logical --k 256 --seed 1 --batch 1024 --sets $SETS --out $O
  echo "$(date -u +%FT%TZ) end $O rc=$?"
done
