#!/usr/bin/env bash
# round3-run4b, after the fixed pipeline of one draw: conditional `mix` arm (pre-registered E6), then the optional-pool pre-RL sample (amendment A1).
# On the pod: bash pod/r3_4b/post.sh <25M|85M> <seed>. Waits for the draw's frozen arm; the optional-pool sample also waits for the retry's Stage-1 (GPU memory).
cd /workspace/nd-takehome
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
SIZE=$1; S=$2
case $SIZE in 25M|25Mr) FTLR=1e-4; CB=2000; EB=1024;; 85M|85Mr) FTLR=3e-5; CB=1000; EB=768;; esac
T=${SIZE}_s${S}; Q=artifacts/r3_4b/q; CK=ckpts/r3_4b/stage1_depth3_f0_a1_$T.pt
PROCS=$(( $(nproc) > 8 ? 8 : $(nproc) ))
stage() { n=$1; shift; [ -f $Q/${n}_$T.done ] && { echo "skip $n"; return 0; }
  echo "$(date -u +%FT%TZ) start $n $T"; bash -c "$*" > $Q/${n}_$T.log 2>&1 && touch $Q/${n}_$T.done && echo "$(date -u +%FT%TZ) done $n $T" || { echo "$(date -u +%FT%TZ) FAILED $n $T"; return 1; }; }
until [ -f $Q/frozen_$T.done ] || [ -f $Q/frozen_$T.skipped ]; do sleep 30; done
stage mix "python3 expert_iter.py --init $CK --name r3_4b/ei_depth3_${T}_mix --targets data/r3_1/depth3_mix.jsonl --transfer data/r3_1/depth3_req_transfer.jsonl --heldout data/p2/heldout.jsonl --train data/p2/train_depth3_f0_a1.jsonl --rounds 8 --k 32 --temperature 0.8 --retain 20000 --ft_steps 600 --ft_lr $FTLR --seed $S --batch $EB"
until [ -f $Q/s1_${SIZE}r_s$S.done ] || [ -f $Q/noretry ] || [ ${SIZE%r} != $SIZE ]; do sleep 30; done
sleep $((RANDOM % 30)); while pgrep -f "coverage.p[y]" > /dev/null; do sleep $((20 + RANDOM % 20)); done   # one pre-RL sampler per GPU at a time
stage optcov "python3 coverage.py --ckpt $CK --in data/p2/targets_depth3.jsonl --limit 300 --out artifacts/r3_4b/optcov_depth3_$T --k 2000 --temperature 0.8 --batch $CB --seed 0 --procs $PROCS"
echo "$(date -u +%FT%TZ) POST DONE $T"
