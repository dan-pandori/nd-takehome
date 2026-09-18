#!/usr/bin/env bash
# round3-run4b E5 retry (pre-registered: lr 1e-4, min 1e-5, 12,000 steps, same seed). On the pod: bash pod/r3_4b/retry.sh <25M|85M> <seed>
# Waits for the draw's pre-RL sample to finish (GPU memory), trains ckpts/r3_4b/stage1_depth3_f0_a1_<size>r_s<seed>.pt, then held-out greedy on 5,000.
cd /workspace/nd-takehome
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
SIZE=$1; S=$2
case $SIZE in 25M) ARCH="--n_layer 8 --d 512 --n_head 8"; EB=1024;; 85M) ARCH="--n_layer 12 --d 768 --n_head 12"; EB=768;; esac
T=${SIZE}_s${S}; R=${SIZE}r_s${S}; Q=artifacts/r3_4b/q; CK=ckpts/r3_4b/stage1_depth3_f0_a1_$R.pt
until [ -f $Q/cov_$T.done ]; do sleep 30; done
echo "$(date -u +%FT%TZ) start s1 $R"
python3 train.py --data data/p2/train_depth3_f0_a1.jsonl --heldout data/p2/heldout.jsonl --mode abs --cap 6 --bs 128 --steps 12000 --lr 1e-4 --min_lr 1e-5 --warmup 500 $ARCH --seed $S --out $CK > $Q/s1_$R.log 2>&1 && touch $Q/s1_$R.done || { echo FAILED s1; exit 1; }
echo "$(date -u +%FT%TZ) start gate $R"
python3 eval_set.py --ckpt $CK --in data/p2/heldout.jsonl --out artifacts/r3_4b/heldout_greedy_$R.jsonl --temperature 0 --batch $EB --summary artifacts/r3_4b/heldout_greedy_$R.json > $Q/gate_$R.log 2>&1 && touch $Q/gate_$R.done
echo "$(date -u +%FT%TZ) RETRY DONE $R"
