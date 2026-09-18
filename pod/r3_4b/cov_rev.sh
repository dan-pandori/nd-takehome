#!/usr/bin/env bash
# round3-run4b: second half of a pre-RL 600k sample, processed in reverse target order on another pod (-> cov_depth3_<T>.s0r.jsonl); same seed-0 generator
# as the forward half, which is stopped when the two meet. On the pod: bash pod/r3_4b/cov_rev.sh <tag> <seed> <batch>
cd /workspace/nd-takehome; mkdir -p artifacts/r3_4b/q
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
T=$1_s$2; Q=artifacts/r3_4b/q; CK=ckpts/r3_4b/stage1_depth3_f0_a1_$T.pt
nohup bash -c "python3 coverage.py --ckpt $CK --in data/r3_1/depth3_req.jsonl --out artifacts/r3_4b/cov_depth3_$T --k 2000 --temperature 0.8 --batch $3 --seed 0 --reverse --procs 8 > $Q/covrev_$T.log 2>&1 && touch $Q/covrev_$T.done" > /dev/null 2>&1 < /dev/null &
disown; echo "launched reverse pre-RL sample $T batch $3"
