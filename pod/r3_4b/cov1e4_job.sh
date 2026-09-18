#!/usr/bin/env bash
# round3-run4b: pass@10^4 on the 300 required targets from a Stage-1 checkpoint (EI-only count; amendment A3), seed 1 (the 600k sample is seed 0).
# On the pod (via cov1e4.sh): bash pod/r3_4b/cov1e4_job.sh <tag> <seed> <shard i/n> <batch> [rev]. Waits until no other sampler runs on the GPU.
# (This is a script file, not a `bash -c` string, so that its own command line does not match the sampler guard.)
cd /workspace/nd-takehome; mkdir -p artifacts/r3_4b/q
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
T=$1_s$2; SH=$3; B=$4; REV=${5:+--reverse}; Q=artifacts/r3_4b/q; CK=ckpts/r3_4b/stage1_depth3_f0_a1_$T.pt; N=cov1e4_${T}_sh${SH%/*}${5:+r}
sleep $((RANDOM % 20)); while pgrep -f "python3 coverage.p[y]" > /dev/null; do sleep 30; done
python3 coverage.py --ckpt $CK --in data/r3_1/depth3_req.jsonl --out artifacts/r3_4b/cov1e4_depth3_$T --k 10000 --temperature 0.8 --batch $B --seed 1 --shard $SH $REV --procs 16 > $Q/$N.log 2>&1 && touch $Q/$N.done
