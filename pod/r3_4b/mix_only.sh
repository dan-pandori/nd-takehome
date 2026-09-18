#!/usr/bin/env bash
# round3-run4b: a mix arm alone on a pod (no co-tenant), batch 768. On the pod: bash pod/r3_4b/mix_only.sh <tag e.g. 85M> <seed>
cd /workspace/nd-takehome; mkdir -p artifacts/r3_4b/q
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
T=$1_s$2; Q=artifacts/r3_4b/q; CK=ckpts/r3_4b/stage1_depth3_f0_a1_$T.pt
case $1 in 25M*) FTLR=1e-4; EB=1024;; *) FTLR=3e-5; EB=768;; esac
nohup bash -c "python3 expert_iter.py --init $CK --name r3_4b/ei_depth3_${T}_mix --targets data/r3_1/depth3_mix.jsonl --transfer data/r3_1/depth3_req_transfer.jsonl --heldout data/p2/heldout.jsonl --train data/p2/train_depth3_f0_a1.jsonl --rounds 8 --k 32 --temperature 0.8 --retain 20000 --ft_steps 600 --ft_lr $FTLR --seed $2 --batch $EB > $Q/mix_$T.log 2>&1 && touch $Q/mix_$T.done" > /dev/null 2>&1 < /dev/null &
disown; echo "launched mix $T"
