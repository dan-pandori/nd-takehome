#!/usr/bin/env bash
# Part B: k 256, T 0.8, seed 0, max_steps 96 re-read of one checkpoint on the textbook theorems of transfer.jsonl (760)
# and transfer_long.jsonl (282). Usage: b.sh <ckpt> <label> [batch]. Restartable per pool.
CK=$1; L=$2; B=${3:-4096}; D=artifacts/state-readouts/rr; mkdir -p $D
for P in tb:data/sr/textbook_transfer.jsonl tbl:data/sr/textbook_long.jsonl; do
  T=${P%%:*}; IN=${P#*:}; O=$D/${L}__$T
  [ -s $O.json ] && continue
  echo "=== reread $L $T $(date -u +%FT%TZ)"
  LEAN_GATE_DUMP=artifacts/state-readouts/dump/rr_${L}__$T.jsonl python3 lpool_reread.py --ckpt $CK --in $IN --k 256 \
    --temperature 0.8 --seed 0 --batch $B --max_action 512 --max_steps 96 --lenfield L_true \
    --out $O.jsonl --summary $O.json || { echo "REREAD FAILED $L $T"; exit 1; }
done
