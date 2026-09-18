#!/usr/bin/env bash
# round3-run4b: pass@10^4 on the 300 required targets from a Stage-1 checkpoint (EI-only count), independent seed (1) from the 600k sample (seed 0).
# On the pod: bash pod/r3_4b/cov1e4.sh <tag> <seed> <shard i/n> <batch> [rev]. With a 5th argument the shard is processed in reverse order (-> .s<i>r.jsonl; stop both when together they cover the shard). Waits until no other coverage.py runs. Output artifacts/r3_4b/cov1e4_depth3_<tag>_s<seed>.s<i>.jsonl
cd /workspace/nd-takehome; mkdir -p artifacts/r3_4b/q
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
T=$1_s$2; SH=$3; B=$4; REV=${5:+--reverse}; Q=artifacts/r3_4b/q; CK=ckpts/r3_4b/stage1_depth3_f0_a1_$T.pt; N=cov1e4_${T}_sh${SH%/*}${5:+r}
nohup bash -c "sleep \$((RANDOM % 20)); while pgrep -f 'coverage.p[y]' > /dev/null; do sleep 30; done; python3 coverage.py --ckpt $CK --in data/r3_1/depth3_req.jsonl --out artifacts/r3_4b/cov1e4_depth3_$T --k 10000 --temperature 0.8 --batch $B --seed 1 --shard $SH $REV --procs 16 > $Q/$N.log 2>&1 && touch $Q/$N.done" > /dev/null 2>&1 < /dev/null &
disown; echo "queued cov1e4 $T shard $SH batch $B"
