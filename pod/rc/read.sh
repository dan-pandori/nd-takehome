#!/usr/bin/env bash
# Sampled read-outs of one checkpoint (trajectory's pod/tj/read.sh + best-state's rr600/long2 reads).
# Usage: bash pod/rc/read.sh <ckpt> <label> <sample seed> <reads...>     reads: tb72 h250 rr1316 long2
# Settings for every read: k 256 (rr1316: k 64, budget, 2026-10-03 20:40 UTC), T 0.8, max_action 512, max_steps 96, batch 2,048 (one retry at 1,024 on OOM).
# Restartable: a read whose summary exists is skipped.
source pod/rc/env.sh
CK=$1; L=$2; SS=$3; shift 3; B=${B:-2048}; MA=512; MS=96
for R in "$@"; do
  O=artifacts/rc/eval/${L}__${R}_x$SS; LG=artifacts/rc/logs/read/${L}__${R}_x$SS.log; [ -s $O.json ] && { echo "skip $L $R x$SS"; continue; }
  echo "=== $L $R x$SS $(date -u +%FT%TZ)"
  run() {
    case $R in
      tb72)   python3 state_eval.py --ckpt $CK --in data/bs/textbook72.jsonl --lenfield reference_lines --k 256 --temperature 0.8 --seed $SS \
                --batch $1 --max_action $MA --max_steps $MS --out $O.jsonl.tmp --summary $O.json.tmp ;;
      h250)   python3 state_eval.py --ckpt $CK --in data/bs/holdout250.jsonl --lenfield n_lines --k 256 --temperature 0.8 --seed $SS \
                --batch $1 --max_action $MA --max_steps $MS --out $O.jsonl.tmp --summary $O.json.tmp ;;
      rr1316) python3 lpool_reread.py --ckpt $CK --in data/rc/rr600_13_16.jsonl --lenfield L_true_lb --k 64 --temperature 0.8 --seed $SS \
                --batch $1 --max_action $MA --max_steps $MS --out $O.jsonl.tmp --summary $O.json.tmp ;;
      long2)  python3 lpool_reread.py --ckpt $CK --in data/ladder/transfer_long2.jsonl --lenfield L_true_lb --k 256 --temperature 0.8 --seed $SS \
                --batch $1 --max_action $MA --max_steps $MS --out $O.jsonl.tmp --summary $O.json.tmp ;;
    esac > $LG 2>&1; }
  BB=$B; case $R in rr1316|long2) BB=${RRB:-512} ;; esac   # rr reads at 512: r8 baseline runs beside a ladder (budget, 2026-10-03 23:40)
  run $BB || { [ "$BB" -gt 1024 ] && grep -q OutOfMemoryError $LG && { echo "=== retry $L $R x$SS at batch 1024"; mv $LG ${LG%.log}.oom$BB.log; run 1024; }; } \
    || { echo "READ FAILED $L $R x$SS"; continue; }
  mv $O.jsonl.tmp $O.jsonl; mv $O.json.tmp $O.json
  echo "=== done $L $R x$SS $(date -u +%FT%TZ) $(grep -m1 -o '"solved": [0-9]*' $O.json)"
done
up artifacts/rc
