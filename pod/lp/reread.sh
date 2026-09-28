#!/usr/bin/env bash
# long-pool re-read queue: bash pod/lp/reread.sh <lane> <model>...   (two lanes run side by side on one 24 GB GPU)
# Fixed across models: k 256, T 0.8, seed 0; whole-proof batch 4096 / max_new 768; state batch 2048 / max_action 256 /
# max_steps 48 (state-env's settings).  IN / SUF env: another pool (the >= 17 file) and an output suffix.  Skips a model whose summary exists (restartable).
cd /workspace/nd-takehome; export PATH=$HOME/.elan/bin:$PATH; mkdir -p artifacts/lp/rr; lane=$1; shift; IN=${IN:-data/ladder/transfer_long_rr600.jsonl}; SUF=${SUF:-}
for m in "$@"; do
  [ -s artifacts/lp/rr/$m$SUF.json ] && continue
  case $m in state-env__*) B=2048;; *) B=4096;; esac
  echo "$(date -u +%FT%TZ) START $m" >> artifacts/lp/rr/queue_$lane.log
  python3 lp_reread.py --ckpt ckpts/lp/$m.pt --in $IN --k 256 --temperature 0.8 --seed 0 \
    --batch $B --max_new 768 --out artifacts/lp/rr/$m$SUF.jsonl --summary artifacts/lp/rr/$m$SUF.json --lenfield L_true_lb > artifacts/lp/rr/$m$SUF.log 2>&1
  echo "$(date -u +%FT%TZ) END $m rc=$?" >> artifacts/lp/rr/queue_$lane.log
done
echo "$(date -u +%FT%TZ) QUEUE DONE" >> artifacts/lp/rr/queue_$lane.log
