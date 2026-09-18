#!/usr/bin/env bash
# round3-run4b: the fixed part of one draw's pipeline, run on the pod. Usage: bash pod/r3_4b/draw.sh <25M|85M> <seed> [stage]
# Stages (each skipped if its .done marker exists): s1 (Stage-1) -> gate (held-out greedy, 5,000) -> cov (pre-RL 600k) -> req (EI) -> frozen (--no_train).
# Logs: artifacts/r3_4b/q/<stage>_<size>_s<seed>.log
cd /workspace/nd-takehome
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
SIZE=$1; S=$2
case $SIZE in
  25M|25Mr) ARCH="--n_layer 8 --d 512 --n_head 8"; FTLR=1e-4; CB=2000; EB=1024;;
  85M|85Mr) ARCH="--n_layer 12 --d 768 --n_head 12"; FTLR=3e-5; CB=1000; EB=768;;
  *) echo "size?"; exit 1;;
esac
T=${SIZE}_s${S}; Q=artifacts/r3_4b/q; CK=ckpts/r3_4b/stage1_depth3_f0_a1_$T.pt
mkdir -p $Q ckpts/r3_4b
PROCS=$(( $(nproc) > 8 ? 8 : $(nproc) ))
stage() { n=$1; shift; [ -f $Q/${n}_$T.done ] && { echo "skip $n"; return 0; }
  echo "$(date -u +%FT%TZ) start $n $T"; bash -c "$*" > $Q/${n}_$T.log 2>&1 && touch $Q/${n}_$T.done && echo "$(date -u +%FT%TZ) done $n $T" || { echo "$(date -u +%FT%TZ) FAILED $n $T"; return 1; }; }
[ -f $Q/s1_$T.done ] || case $SIZE in *r) echo "retry checkpoints are trained by retry.sh"; exit 1;; esac
stage s1 "python3 train.py --data data/p2/train_depth3_f0_a1.jsonl --heldout data/p2/heldout.jsonl --mode abs --cap 6 --bs 128 --steps 6000 --lr 3e-4 --min_lr 3e-5 --warmup 500 $ARCH --seed $S --out $CK" || exit 1
stage gate "python3 eval_set.py --ckpt $CK --in data/p2/heldout.jsonl --out artifacts/r3_4b/heldout_greedy_$T.jsonl --temperature 0 --batch $EB --summary artifacts/r3_4b/heldout_greedy_$T.json" || exit 1
PAR=${PAR:-$([ ${SIZE%r} = 25M ] && echo 1 || echo 0)}   # 1: pre-RL sample shares the GPU with the arms (memory checked on the first pod before use at 85M)
if [ $PAR = 1 ]; then stage cov "python3 coverage.py --ckpt $CK --in data/r3_1/depth3_req.jsonl --out artifacts/r3_4b/cov_depth3_$T --k 2000 --temperature 0.8 --batch $CB --seed 0 --procs $PROCS" & else stage cov "python3 coverage.py --ckpt $CK --in data/r3_1/depth3_req.jsonl --out artifacts/r3_4b/cov_depth3_$T --k 2000 --temperature 0.8 --batch $CB --seed 0 --procs $PROCS" || exit 1; fi
stage req "python3 expert_iter.py --init $CK --name r3_4b/ei_depth3_${T}_req --targets data/r3_1/depth3_req.jsonl --transfer data/r3_1/depth3_req_transfer.jsonl --heldout data/p2/heldout.jsonl --train data/p2/train_depth3_f0_a1.jsonl --rounds 8 --k 32 --temperature 0.8 --retain 20000 --ft_steps 600 --ft_lr $FTLR --seed $S --batch $EB"
# a req arm that never trained makes the frozen arm a bit-identical copy of it (checked on the three 25M draws): skip it then, with a marker
TR=$(python3 -c "import json,glob; print(sum(json.load(open(f)).get('mix_rl_records',0)>0 for f in glob.glob('artifacts/r3_4b/ei_depth3_${T}_req/round_*.json')))")
if [ "$TR" = 0 ] && [ -f $Q/req_$T.done ]; then echo "$(date -u +%FT%TZ) req arm never trained: frozen arm skipped (identical to req by construction)" > $Q/frozen_$T.skipped
else stage frozen "python3 expert_iter.py --init $CK --name r3_4b/ei_depth3_${T}_frozen --no_train --targets data/r3_1/depth3_req.jsonl --transfer data/r3_1/depth3_req_transfer.jsonl --heldout data/p2/heldout.jsonl --train data/p2/train_depth3_f0_a1.jsonl --rounds 8 --k 32 --temperature 0.8 --seed $S --batch $EB"
fi
wait
echo "$(date -u +%FT%TZ) DRAW DONE $T"
