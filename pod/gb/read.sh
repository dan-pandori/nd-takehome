#!/usr/bin/env bash
# Read-outs of one checkpoint (trajectory's / best-state's settings).  Usage: bash pod/gb/read.sh <ckpt> <label> <sample seed> <reads...>
#   reads: tb72 h250 (k 256, T 0.8, max_action 512, max_steps 96)   dev (dev1108, k 64, seed 0)   held (held-out greedy, k 1, T 0)
# Restartable: a read whose summary exists is skipped.  One retry at batch 1,024 after a CUDA OOM.
source pod/gb/env.sh
CK=$1; L=$2; SS=$3; shift 3; B=${B:-2048}; MA=${MA:-512}; MS=${MS:-96}; mkdir -p artifacts/gb/eval artifacts/gb/logs/read
for R in "$@"; do
  O=artifacts/gb/eval/${L}__${R}_x$SS; [ -s $O.json ] && { echo "skip $L $R x$SS"; continue; }
  echo "=== $L $R x$SS $(date -u +%FT%TZ)"
  for BB in $B 1024; do
    case $R in
      tb72) A="--in data/bs/textbook72.jsonl --k 256 --temperature 0.8 --seed $SS --max_action $MA --max_steps $MS --lenfield reference_lines" ;;
      h250) A="--in data/bs/holdout250.jsonl --k 256 --temperature 0.8 --seed $SS --max_action $MA --max_steps $MS --lenfield n_lines" ;;
      dev)  A="--in data/bs/dev1108.jsonl --k 64 --temperature 0.8 --seed $SS --max_action $MA --max_steps $MS --lenfield n_lines" ;;
      held) A="--in data/p2/heldout.jsonl --k 1 --temperature 0" ;;
    esac
    LG=artifacts/gb/logs/read/${L}__${R}_x$SS.log
    ND_ARM=$L python3 state_eval.py --ckpt $CK $A --batch $BB --out $O.jsonl.tmp --summary $O.json.tmp > $LG 2>&1 && break
    grep -q OutOfMemoryError $LG && [ $BB != 1024 ] && { mv $LG $LG.oom$BB; echo "=== retry $L $R x$SS at 1024"; continue; }
    break
  done
  [ -s $O.json.tmp ] || { echo "READ FAILED $L $R x$SS"; continue; }
  mv $O.jsonl.tmp $O.jsonl; mv $O.json.tmp $O.json
  echo "=== done $L $R x$SS $(date -u +%FT%TZ) $(grep -m1 -o '"solved": [0-9]*' $O.json)"
done
up artifacts/gb
