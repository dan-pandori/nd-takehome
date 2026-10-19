#!/usr/bin/env bash
# KAL-D pod, after training: the final model's greedy read-outs, then the learning curve (teacher-forced agreement and
# greedy free generation on tf1200 for every snapshot).  Usage: bash pod/kal/post_D.sh <seed>
cd /workspace/nd-takehome; . pod/kal/env.sh
S=$1
until [ -f artifacts/kalmar/logs/train_kalD_s$S.done ]; do sleep 60; done
bash pod/kal/eval_greedy.sh kalD_s$S ckpts/kalmar/stage1_kalD_s$S.pt kal 1024
M=artifacts/kalmar/markers; L=artifacts/kalmar/logs
for st in 24020 100000 200000 350000 500000; do
  C=ckpts/kalmar/stage1_kalD_s${S}_step$st.pt; T=kalD_s${S}_step$st
  [ -s $C ] || continue
  [ -f $M/tf_$T.done ] || { python3 kalmar/tf_agree.py --ckpt $C --in data/kalmar/tf1200_kal_sl.jsonl --out artifacts/kalmar/tf/${T}__tf1200.json --batch 1024 > $L/tf_$T.log 2>&1 && touch $M/tf_$T.done; }
  [ -f $M/fg_$T.done ] || { python3 kalmar/kal_free.py --ckpt $C --in data/kalmar/tf1200_kal_sl.jsonl --k 1 --temperature 0 --out artifacts/kalmar/free/${T}__tf1200_greedy.json --max_steps 1024 --max_action 512 --batch 1024 > $L/fg_$T.log 2>&1 && touch $M/fg_$T.done; }
done
up artifacts/kalmar/tf; up artifacts/kalmar/free; up artifacts/kalmar/logs
touch $M/post_D_s$S.done
