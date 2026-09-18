#!/usr/bin/env bash
# round3-run4b: optional-pool pre-RL sample (amendment A1) for one checkpoint. On the pod: bash pod/r3_4b/optcov_only.sh <tag> <seed> <batch>
cd /workspace/nd-takehome; mkdir -p artifacts/r3_4b/q
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
T=$1_s$2; Q=artifacts/r3_4b/q; CK=ckpts/r3_4b/stage1_depth3_f0_a1_$T.pt
nohup bash -c "python3 coverage.py --ckpt $CK --in data/p2/targets_depth3.jsonl --limit 300 --out artifacts/r3_4b/optcov_depth3_$T --k 2000 --temperature 0.8 --batch $3 --seed 0 --procs 8 > $Q/optcov_$T.log 2>&1 && touch $Q/optcov_$T.done" > /dev/null 2>&1 < /dev/null &
disown; echo "launched optcov $T batch $3"
