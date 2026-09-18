#!/usr/bin/env bash
# round3-run4b: resume a mix arm whose fine-tune step died (OOM) after round R-1. On the pod: bash pod/r3_4b/mix_resume.sh <tag> <seed> <R> <batch> <ft_lr>
# Round R is re-sampled from the round R-1 checkpoint with the same per-round seed and batch; found_<R-1>.jsonl is reloaded (--resume_found).
cd /workspace/nd-takehome
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
T=$1_s$2; R=$3; B=$4; FTLR=$5; Q=artifacts/r3_4b/q; D=artifacts/r3_4b/ei_depth3_${T}_mix
cp $D/args.json $D/args_rounds1-$((R-1)).json; cp $Q/mix_$T.log $Q/mix_$T.rounds1-$((R-1)).log
nohup bash -c "python3 expert_iter.py --init ckpts/r3_4b/ei_depth3_${T}_mix_r$((R-1)).pt --start_round $R --rounds $((9-R)) --resume_found $D --name r3_4b/ei_depth3_${T}_mix --targets data/r3_1/depth3_mix.jsonl --transfer data/r3_1/depth3_req_transfer.jsonl --heldout data/p2/heldout.jsonl --train data/p2/train_depth3_f0_a1.jsonl --k 32 --temperature 0.8 --retain 20000 --ft_steps 600 --ft_lr $FTLR --seed $2 --batch $B > $Q/mix_$T.log 2>&1 && touch $Q/mix_$T.done" > /dev/null 2>&1 < /dev/null &
disown; echo "resumed mix $T from round $R"
