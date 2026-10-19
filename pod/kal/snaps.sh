#!/usr/bin/env bash
# Teacher-forced agreement + greedy tf1200 for KAL-D snapshots (fetched from the bucket).  Usage: bash pod/kal/snaps.sh <step> ...
cd /workspace/nd-takehome; . pod/kal/env.sh
M=artifacts/kalmar/markers; L=artifacts/kalmar/logs
for st in "$@"; do for S in 0 1 2; do
  C=ckpts/kalmar/stage1_kalD_s${S}_step$st.pt; T=kalD_s${S}_step$st
  until [ -s $C ]; do hf buckets cp $BK/kalmar-pretrain/$C $C > /dev/null 2>&1 || sleep 60; done
  [ -f $M/tf_$T.done ] || { python3 kalmar/tf_agree.py --ckpt $C --in data/kalmar/tf1200_kal_sl.jsonl --out artifacts/kalmar/tf/${T}__tf1200.json --batch 1024 > $L/tf_$T.log 2>&1 && touch $M/tf_$T.done; }
  [ -f $M/fg_$T.done ] || { python3 kalmar/kal_free.py --ckpt $C --in data/kalmar/tf1200_kal_sl.jsonl --k 1 --temperature 0 --out artifacts/kalmar/free/${T}__tf1200_greedy.json --max_steps 1024 --max_action 512 --batch 1024 > $L/fg_$T.log 2>&1 && touch $M/fg_$T.done; }
done; done
up artifacts/kalmar/tf; up artifacts/kalmar/free; up artifacts/kalmar/logs
echo SNAPS_DONE >> $L/snaps.log
