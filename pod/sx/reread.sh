#!/usr/bin/env bash
# k 256 read-out of one checkpoint WITHOUT search (lpool_reread.py, state_cap12 / long-pool settings, max_steps 96):
# the 91 (transfer_long2 + calibration) and rr600 L_true 13-16.  Usage: bash pod/sx/reread.sh <ckpt> <label>.  Restartable.
source pod/sx/env.sh
CK=$1; L=$2; mkdir -p artifacts/sx/rr
for P in l2:data/ladder/transfer_long2_91.jsonl rr1316:data/ladder/rr600_13to16.jsonl; do
  T=${P%%:*}; IN=${P#*:}; O=artifacts/sx/rr/${L}__$T
  [ -s $O.json ] && continue
  echo "=== reread $L $T $(date -u +%FT%TZ)"
  ND_ARM=rr_$L LEAN_GATE_DUMP=artifacts/sx/dump/rr_${L}__$T.jsonl LEAN_GATE_LOG=artifacts/sx/gate_rr_$L.jsonl python3 lpool_reread.py \
    --ckpt $CK --in $IN --k 256 --temperature 0.8 --seed 0 --batch 2048 --max_action 512 --max_steps 96 --lenfield L_true_lb \
    --out $O.jsonl --summary $O.json > $O.log 2>&1 || echo "REREAD FAILED $L $T"
done
