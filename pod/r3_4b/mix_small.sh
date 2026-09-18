#!/usr/bin/env bash
# round3-run4b: 85M mix arm with sampling batch 384 (batch 768 ran out of memory next to the retry's Stage-1 training). On the pod: bash pod/r3_4b/mix_small.sh <85M|85Mr> <seed>
cd /workspace/nd-takehome
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
T=$1_s$2; Q=artifacts/r3_4b/q; CK=ckpts/r3_4b/stage1_depth3_f0_a1_$T.pt
[ -f $Q/mix_$T.log ] && mv $Q/mix_$T.log $Q/mix_$T.oom1.log; rm -rf artifacts/r3_4b/ei_depth3_${T}_mix.oom1; [ -d artifacts/r3_4b/ei_depth3_${T}_mix ] && mv artifacts/r3_4b/ei_depth3_${T}_mix artifacts/r3_4b/ei_depth3_${T}_mix.oom1
nohup python3 expert_iter.py --init $CK --name r3_4b/ei_depth3_${T}_mix --targets data/r3_1/depth3_mix.jsonl --transfer data/r3_1/depth3_req_transfer.jsonl --heldout data/p2/heldout.jsonl --train data/p2/train_depth3_f0_a1.jsonl --rounds 8 --k 32 --temperature 0.8 --retain 20000 --ft_steps 600 --ft_lr 3e-5 --seed $2 --batch 384 > $Q/mix_$T.log 2>&1 < /dev/null && touch $Q/mix_$T.done &
disown; echo "launched mix (batch 384) $T"
