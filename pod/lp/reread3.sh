#!/usr/bin/env bash
# long-pool re-read, pass 2 (caps raised after pass 1 truncated > 0.1 % of samples in some bins):
#   state: batch 2048, max_action 512, max_steps 48;  whole-proof: batch 1024, max_new 1536;  k 256, T 0.8, seed 0.
# Usage: IN=<pool> SUF=<suffix> bash pod/lp/reread3.sh <lane> <model>...   Outputs artifacts/lp/rr2/<model><SUF>.*
cd /workspace/nd-takehome; export PATH=$HOME/.elan/bin:$PATH; mkdir -p artifacts/lp/rr2; lane=$1; shift
IN=${IN:-data/ladder/transfer_long_rr600.jsonl}; SUF=${SUF:-}
for m in "$@"; do
  [ -s artifacts/lp/rr2/$m$SUF.json ] && continue
  case $m in state-env__*) X="--batch 2048 --max_action 512";; *) X="--batch 1024 --max_new 1536";; esac
  echo "$(date -u +%FT%TZ) START $m$SUF" >> artifacts/lp/rr2/queue_$lane.log
  python3 lp_reread.py --ckpt ckpts/lp/$m.pt --in $IN --k 256 --temperature 0.8 --seed 0 $X --lenfield L_true_lb \
    --out artifacts/lp/rr2/$m$SUF.jsonl --summary artifacts/lp/rr2/$m$SUF.json > artifacts/lp/rr2/$m$SUF.log 2>&1
  echo "$(date -u +%FT%TZ) END $m$SUF rc=$?" >> artifacts/lp/rr2/queue_$lane.log
done
echo "$(date -u +%FT%TZ) QUEUE DONE" >> artifacts/lp/rr2/queue_$lane.log
