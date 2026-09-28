#!/usr/bin/env bash
# lean-prefilter test (c): one T1 ladder round (noise-floor's la_T1_dsc_a1_s1 arguments, --rounds 1), three arms, in
# sequence, alone on the pod.  A = the pre-2026-09-28 path; B = new path at A's batch (accepted set must equal A's);
# C = new path at batch 4096.  Usage: bash pod/lp/t1.sh [arms...]   (default: A B C)
cd /workspace/nd-takehome; mkdir -p artifacts/lp/t1 artifacts/lp/logs
export PATH=$HOME/.elan/bin:$PATH OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
COMMON="--init ckpts/dsc/stage1_a1_s1.pt --outdir artifacts/lp/t1 --targets data/ladder/rl_targets.jsonl --transfer data/ladder/transfer.jsonl --heldout data/p2/heldout.jsonl --train data/dsc/train_a1.jsonl --rounds 1 --k 32 --temperature 0.8 --max_new 512 --seed 1 --alloc uniform"
for arm in ${@:-A B C}; do
  [ -e artifacts/lp/logs/t1_$arm.log ] && { echo "skip $arm (log exists)"; continue; }
  case $arm in
    A) E="LEAN_GATE_WORKERS=3 LEAN_PREFILTER=off LEAN_GATE_PIPELINE=0 ND_SAMPLE_COMPACT=0"; BATCH=512 ;;
    B) E="LEAN_PREFILTER=on LEAN_GATE_PIPELINE=1 ND_SAMPLE_COMPACT=0"; BATCH=512 ;;
    C) E="LEAN_PREFILTER=on LEAN_GATE_PIPELINE=1"; BATCH=4096 ;;
  esac
  echo "$(date -u +%FT%TZ) start $arm $E batch $BATCH"
  env $E LEAN_GATE_LOG=artifacts/lp/t1/gate_$arm.jsonl LEAN_GATE_DUMP=artifacts/lp/t1/dump_$arm.jsonl \
    python3 -u ladder_ei.py $COMMON --name t1_$arm --batch $BATCH > artifacts/lp/logs/t1_$arm.log 2>&1; rc=$?
  echo "$(date -u +%FT%TZ) end $arm rc=$rc"
done
echo "T1 DONE $(date -u +%FT%TZ)"
