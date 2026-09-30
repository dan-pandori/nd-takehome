#!/usr/bin/env bash
# Read-out of one checkpoint: k 256, T 0.8, seed 0, batch 2048, max_action 512, max_steps 96 (long-pool-2's settings)
# on long-pool-2's 91 (transfer_long2 + calib) and rr600 L_true 13-16.  Restartable.  Usage: bash pod/fsup/reread.sh <ckpt> <label>
source pod/fsup/env.sh
CK=$1; L=$2
for P in ${PAIRS:-lp2:data/fsup/lp2_91.jsonl rr:data/fsup/rr600_13_16.jsonl}; do
  T=${P%%:*}; IN=${P#*:}; O=artifacts/fsup/rr/${L}__$T
  [ -s $O.json ] && continue
  echo "=== reread $L $T $(date -u +%FT%TZ)"
  ND_ARM=rr_$L python3 lpool_reread.py --ckpt $CK --in $IN --k 256 --temperature 0.8 --seed 0 --batch 2048 --max_new 1536 \
    --max_action 512 --max_steps 96 --lenfield L_true_lb --out $O.jsonl --summary $O.json > $O.log 2>&1 || echo "REREAD FAILED $L $T"
done
up artifacts/fsup/rr
