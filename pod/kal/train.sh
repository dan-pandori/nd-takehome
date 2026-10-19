#!/usr/bin/env bash
# One Stage-1 job.  Usage: bash pod/kal/train.sh <D|C> <seed>
#   D = data-matched (3.675 epochs of pairs, the control's mean), C = compute-matched (24,020 steps, the control's mean)
. pod/kal/env.sh
ARM=$1; S=$2; L=artifacts/kalmar/logs/train_kal${ARM}_s$S.log
if [ "$ARM" = D ]; then EXTRA="--best_epochs 3.675 --save_at 24020,100000,200000,350000,500000 --curve_every 600"
else EXTRA="--best_steps 24020 --curve_every 60"; fi
date -u +"START %FT%TZ" > $L
python3 state_train.py --recipe best --mode lean_staten --data data/kalmar/train_kal_sl.jsonl \
  --heldout data/kalmar/val300_kal_sl.jsonl --cap 0 --seed $S --load_procs 16 $EXTRA \
  --out ckpts/kalmar/stage1_kal${ARM}_s$S.pt >> $L 2>&1
echo "rc=$?" >> $L; date -u +"END %FT%TZ" >> $L
up artifacts/kalmar/logs
touch artifacts/kalmar/logs/train_kal${ARM}_s$S.done
