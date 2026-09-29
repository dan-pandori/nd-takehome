#!/usr/bin/env bash
# long-pool-2 re-read of one checkpoint on a list of pools.  Usage: reread.sh <ckpt> <label> <tag:file> [<tag:file> ...]
# Settings: k 256, T 0.8, seed 0; state batch 2048 / max_action 512 / max_steps 96; whole-proof (WP=1) batch 1024 /
# max_new 1536 (long-pool pass 2 / state-cap12, with max_steps raised to 96).  Restartable; literal texts dumped.
CK=$1; L=$2; shift 2; mkdir -p artifacts/lpool2/rr artifacts/lpool2/dump
for P in "$@"; do
  T=${P%%:*}; IN=${P#*:}; O=artifacts/lpool2/rr/${L}__${T}
  [ -s $O.json ] && continue
  echo "=== reread $L $T $(date -u +%FT%TZ)"
  LEAN_GATE_DUMP=artifacts/lpool2/dump/rr_${L}__$T.jsonl python3 lpool_reread.py --ckpt $CK --in $IN --k 256 --temperature 0.8 --seed 0 \
    --batch $( [ -n "$WP" ] && echo 1024 || echo 2048 ) --max_new 1536 --max_action 512 --max_steps 96 --lenfield ${LF:-L_true_lb} \
    --out $O.jsonl --summary $O.json > $O.log 2>&1 || echo "REREAD FAILED $L $T"
  echo "=== done $L $T $(date -u +%FT%TZ)"
done
