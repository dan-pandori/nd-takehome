#!/usr/bin/env bash
# Sampled read-outs of one checkpoint.  Usage: bash pod/rfc/read.sh <ckpt> <label> <sample seed> <reads...>   reads: tb72 h250
# trajectory's pod/rfc/read.sh with rl-from-ckpt paths.  Settings (fixed for every checkpoint, best-state's): k 256, T 0.8, max_action 512, max_steps 96, batch 2,048.
# Restartable: a read whose summary exists is skipped.  DUMP=1 keeps the literal text of every sample (gzipped; bucket only).
source pod/rfc/env.sh
CK=$1; L=$2; SS=$3; shift 3; B=${B:-2048}; MA=${MA:-512}; MS=${MS:-96}; mkdir -p artifacts/rfc/eval artifacts/rfc/logs/read
for R in "$@"; do
  O=artifacts/rfc/eval/${L}__${R}_x$SS; [ -s $O.json ] && { echo "skip $L $R x$SS"; continue; }
  echo "=== $L $R x$SS $(date -u +%FT%TZ)"
  if [ "${DUMP:-0}" = 1 ]; then export LEAN_GATE_DUMP=artifacts/rfc/dump/${L}__${R}_x$SS.jsonl; else unset LEAN_GATE_DUMP; fi
  case $R in
    tb72) IN=data/bs/textbook72.jsonl; LF=reference_lines ;;
    h250) IN=data/bs/holdout250.jsonl; LF=n_lines ;;
  esac
  python3 state_eval.py --ckpt $CK --in $IN --k 256 --temperature 0.8 --seed $SS --batch $B --max_action $MA --max_steps $MS \
    --lenfield $LF --out $O.jsonl.tmp --summary $O.json.tmp > artifacts/rfc/logs/read/${L}__${R}_x$SS.log 2>&1 \
    || { [ "$B" != 1024 ] && grep -q OutOfMemoryError artifacts/rfc/logs/read/${L}__${R}_x$SS.log && {   # prefill OOM on long states:
           echo "=== retry $L $R x$SS at batch 1024 (OOM at $B)"                                     # one retry at 1,024 (summary 'batch')
           mv artifacts/rfc/logs/read/${L}__${R}_x$SS.log artifacts/rfc/logs/read/${L}__${R}_x$SS.oom$B.log
           python3 state_eval.py --ckpt $CK --in $IN --k 256 --temperature 0.8 --seed $SS --batch 1024 --max_action $MA --max_steps $MS \
             --lenfield $LF --out $O.jsonl.tmp --summary $O.json.tmp > artifacts/rfc/logs/read/${L}__${R}_x$SS.log 2>&1; }; } \
    || { echo "READ FAILED $L $R x$SS"; continue; }
  mv $O.jsonl.tmp $O.jsonl; mv $O.json.tmp $O.json
  [ -n "$LEAN_GATE_DUMP" ] && [ -s $LEAN_GATE_DUMP ] && gzip -f $LEAN_GATE_DUMP
  echo "=== done $L $R x$SS $(date -u +%FT%TZ) $(grep -m1 -o '"solved": [0-9]*' $O.json)"
done
up artifacts/rfc
