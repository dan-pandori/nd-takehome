#!/usr/bin/env bash
# Phase A read-outs of one checkpoint on some pools: plain sampling (trajectory's k 256 protocol: T 0.8, max_action 512,
# max_steps 96, batch 2,048, sample seed 2), then PUCT without and with the value at the sampling read's wall clock.
# Usage: bash pod/mcts/read.sh <seed> <pend|r8> <pools...>   pools: C tb72 h250 rrQ100 long2 tune200
# Restartable: a read whose summary exists is skipped (its wall clock is reused as the budget).
source pod/mcts/env.sh
S=$1; C=$2; shift 2
case $C in pend) CK=ckpts/mcts/stage1_best12_s${S}_b1200.pt ;; r8) CK=ckpts/mcts/la_T1_best12_s${S}_r8.pt ;; esac
CFG=${CFG:-artifacts/mcts/cfg_final.json}
ARMS=${ARMS:-prior value}
for P in "$@"; do
  IN=data/mcts/$P.jsonl; [ $P = C ] && IN=data/mcts/groupC_s$S.jsonl
  O=artifacts/mcts/eval/s${S}_${C}__$P
  if [ ! -s ${O}__sample.json ]; then
    echo "=== sample s$S $C $P $(ts)"
    nvidia-smi --query-gpu=utilization.gpu --format=csv,noheader,nounits -l 1 > ${O}__sample.util & UP=$!
    python3 state_eval.py --ckpt $CK --in $IN --k 256 --temperature 0.8 --seed 2 --batch 2048 --max_action 512 --max_steps 96 \
      --lenfield len --out ${O}__sample.jsonl.tmp --summary ${O}__sample.json.tmp > artifacts/mcts/logs/s${S}_${C}__${P}__sample.log 2>&1 \
      || { kill $UP 2>/dev/null; echo "SAMPLE FAILED $P"; continue; }
    kill $UP 2>/dev/null
    mv ${O}__sample.jsonl.tmp ${O}__sample.jsonl; mv ${O}__sample.json.tmp ${O}__sample.json
  fi
  W=$(python3 -c "import json;print(json.load(open('${O}__sample.json'))['wall_s'])")
  for A in $ARMS; do
    TAG=${TAGSUF:-}
    [ -s ${O}__$A$TAG.json ] && { echo "skip $A$TAG $P"; continue; }
    J=$(python3 -c "import json,sys;print(json.dumps(json.load(open('$CFG'))['$A']))")
    echo "=== search $A$TAG s$S $C $P budget ${W}s $(ts) cfg $J"
    python3 mcts_eval.py --ckpt $CK --in $IN --arm $A --value ckpts/mcts/value_s${S}_$C.pt --budget_s $W --seed $S \
      --cfg "$J" --out ${O}__$A$TAG.jsonl > artifacts/mcts/logs/s${S}_${C}__${P}__$A$TAG.log 2>&1 || echo "SEARCH FAILED $A $P"
    grep SUMMARY artifacts/mcts/logs/s${S}_${C}__${P}__$A$TAG.log | cut -c1-300
  done
  up artifacts/mcts
done
