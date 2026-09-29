#!/usr/bin/env bash
# long-pool pass-2 re-read of one checkpoint on rr600, the >= 17 file and (optionally) the original transfer pool.
# Usage: bash pod/sc12/reread.sh <ckpt> <label> [orig]   Settings = long-pool pass 2 (k 256, T 0.8, seed 0;
# state batch 2048 / max_action 512 / max_steps 48; whole-proof batch 1024 / max_new 1536).  Restartable.
source pod/sc12/env.sh
CK=$1; L=$2; mkdir -p artifacts/sc12/rr
for P in rr600:data/ladder/transfer_long_rr600.jsonl ge17:data/ladder/transfer_long_ge17.jsonl ${3:+orig:data/ladder/transfer.jsonl}; do
  T=${P%%:*}; IN=${P#*:}; O=artifacts/sc12/rr/${L}__$T
  [ -s $O.json ] && continue
  echo "=== reread $L $T $(date -u +%FT%TZ)"
  LEAN_GATE_DUMP=artifacts/sc12/dump/rr_${L}__$T.jsonl python3 lpool_reread.py --ckpt $CK --in $IN --k 256 --temperature 0.8 --seed 0 \
    --batch $( [ -n "$WP" ] && echo 1024 || echo 2048 ) --max_new 1536 --max_action 512 --max_steps 48 --lenfield L_true_lb \
    --out $O.jsonl --summary $O.json > $O.log 2>&1 || echo "REREAD FAILED $L $T"
done
up artifacts/sc12
