#!/usr/bin/env bash
# round3-run4a Stage-1 + held-out greedy gate for one draw. usage: bash pod/r3_4a/stage1.sh <size: m3|m25|m85> <seed> [cfg: A|B]
# cfg A = brief's first configuration (lr 3e-4, min 3e-5, warmup 500, 6000 steps); cfg B = the one allowed retry (lr 1e-4, min 1e-5, 12000 steps).
# m3 = the campaign's 3.2M command unchanged (default lr 1e-3, warmup 200), the same-set control.
set -e
cd /workspace/nd-takehome
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
SZ=$1; S=$2; CFG=${3:-A}
case $SZ in
  m3)  ARCH="--n_layer 4 --d 256 --n_head 8";;
  m25) ARCH="--n_layer 8 --d 512 --n_head 8";;
  m85) ARCH="--n_layer 12 --d 768 --n_head 12";;
esac
if [ $SZ = m3 ]; then HP="--steps 6000"; TAG=${SZ}_s$S
elif [ $CFG = A ]; then HP="--steps 6000 --lr 3e-4 --min_lr 3e-5 --warmup 500"; TAG=${SZ}_s$S
else HP="--steps 12000 --lr 1e-4 --min_lr 1e-5 --warmup 500"; TAG=${SZ}B_s$S; fi
CK=ckpts/r3_4a/stage1_reductio_f0_b1_$TAG.pt
A=artifacts/r3_4a
if [ ! -f $CK ]; then
  python3 train.py --data data/r3_4a/train_reductio_f0_b1.jsonl --heldout data/p2/heldout.jsonl --mode abs --bs 128 --cap 6 $ARCH $HP --seed $S --out $CK > $A/train_$TAG.log 2>&1
fi
python3 eval_set.py --ckpt $CK --in data/p2/heldout.jsonl --out $A/heldout_greedy_$TAG.jsonl --temperature 0 --summary $A/heldout_greedy_$TAG.json > $A/heldout_greedy_$TAG.log 2>&1
touch $A/stage1_$TAG.done
