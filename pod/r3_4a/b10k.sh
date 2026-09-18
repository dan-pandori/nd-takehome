#!/usr/bin/env bash
# round3-run4a: base reachability at pass@1e4 (Stage-1 checkpoint, fresh seed 1) on the targets the draw's EI arm acquired.
# usage: bash pod/r3_4a/b10k.sh <tag> [batch]
set -e
cd /workspace/nd-takehome
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
TAG=$1; B=${2:-2000}; A=artifacts/r3_4a
[ -f $A/b10k_$TAG.done ] && exit 0
python3 r3_4a_acquired.py $TAG > $A/acq_$TAG.log 2>&1
if [ -s data/r3_4a/acq_$TAG.jsonl ]; then
  python3 coverage.py --ckpt ckpts/r3_4a/stage1_reductio_f0_b1_$TAG.pt --in data/r3_4a/acq_$TAG.jsonl --out $A/cov_${TAG}_b10k --k 10000 --temperature 0.8 --seed 1 --batch $B --procs 8 --lenfield min_lines_ub > $A/cov_${TAG}_b10k.log 2>&1
fi
touch $A/b10k_$TAG.done
