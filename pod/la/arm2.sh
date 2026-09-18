#!/usr/bin/env bash
# One ladder arm (memory-safe launch: expandable CUDA segments, batch 384), then base-reachability scoring.
# Usage: bash pod/la/arm2.sh <name> [ladder_ei args...]   Log: artifacts/ladder/<name>.log ; marker artifacts/ladder/<name>.done
cd /workspace/nd-takehome; export OMP_NUM_THREADS=4; export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
NAME=$1; shift
[ -f data/train.jsonl ] || gunzip -k data/train.jsonl.gz
python3 ladder_ei.py --init ckpts/stage1_abs.pt --name $NAME --batch 384 "$@" > artifacts/ladder/$NAME.log 2>&1 || { echo FAILED >> artifacts/ladder/$NAME.log; exit 1; }
bash pod/la/novelty.sh $NAME >> artifacts/ladder/$NAME.log 2>&1
touch artifacts/ladder/$NAME.done
