#!/usr/bin/env bash
# round3-run4b: run sampler jobs strictly one after another on this pod (one coverage.py holds 23-25 GB). On the pod: bash pod/r3_4b/seq.sh <name> "<job>" "<job>" ...
# job = "<kind> <tag> <seed> <batch>", kind in: opt (optional pool, 600k) | rev (required pool, reverse half) | fwd (required pool, forward) | e4 / e4r (pass@10^4 fwd / reverse)
cd /workspace/nd-takehome; mkdir -p artifacts/r3_4b/q
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
NAME=$1; shift
( for job in "$@"; do set -- $job; K=$1; T=$2_s$3; B=$4; CK=ckpts/r3_4b/stage1_depth3_f0_a1_$T.pt; Q=artifacts/r3_4b/q
    while pgrep -f "python3 coverage.p[y]" > /dev/null; do sleep 20; done
    case $K in
      opt) python3 coverage.py --ckpt $CK --in data/p2/targets_depth3.jsonl --limit 300 --out artifacts/r3_4b/optcov_depth3_$T --k 2000 --temperature 0.8 --batch $B --seed 0 --procs 8 >> $Q/optcov_$T.log 2>&1 && touch $Q/optcov_$T.done;;
      rev) python3 coverage.py --ckpt $CK --in data/r3_1/depth3_req.jsonl --out artifacts/r3_4b/cov_depth3_$T --k 2000 --temperature 0.8 --batch $B --seed 0 --reverse --procs 8 >> $Q/covrev_$T.log 2>&1 && touch $Q/covrev_$T.done;;
      fwd) python3 coverage.py --ckpt $CK --in data/r3_1/depth3_req.jsonl --out artifacts/r3_4b/cov_depth3_$T --k 2000 --temperature 0.8 --batch $B --seed 0 --procs 8 >> $Q/cov_$T.log 2>&1 && touch $Q/cov_$T.done;;
      e4)  python3 coverage.py --ckpt $CK --in data/r3_1/depth3_req.jsonl --out artifacts/r3_4b/cov1e4_depth3_$T --k 10000 --temperature 0.8 --batch $B --seed 1 --procs 16 >> $Q/cov1e4_${T}_sh0.log 2>&1 && touch $Q/cov1e4_${T}_sh0.done;;
      e4r) python3 coverage.py --ckpt $CK --in data/r3_1/depth3_req.jsonl --out artifacts/r3_4b/cov1e4_depth3_$T --k 10000 --temperature 0.8 --batch $B --seed 1 --reverse --procs 16 >> $Q/cov1e4_${T}_sh0r.log 2>&1 && touch $Q/cov1e4_${T}_sh0r.done;;
    esac; echo "$(date -u +%FT%TZ) finished $job"
  done; echo "$(date -u +%FT%TZ) SEQ DONE" ) > artifacts/r3_4b/q/seq_$NAME.log 2>&1 < /dev/null &
disown; echo "queued: $*"
