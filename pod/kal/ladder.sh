#!/usr/bin/env bash
# EI ladder from a KAL-D base (pre-registration Addendum 1).  Usage: bash pod/kal/ladder.sh <ei|frozen> <seed> [extra args]
. pod/kal/env.sh
ARM=$1; S=$2; shift 2
NAME=la_kal_${ARM}_s$S
CK=${INIT:-ckpts/kalmar/stage1_kalD_s$S.pt}
until [ -s $CK ]; do hf buckets cp $BK/kalmar-pretrain/$CK $CK > /dev/null 2>&1 || sleep 60; done
mkdir -p artifacts/kalmar/ladder ckpts/kalmar/ladder artifacts/kalmar/dump
export LEAN_GATE_DUMP=artifacts/kalmar/dump/${NAME}.jsonl
X=""; [ $ARM = frozen ] && X="--no_train"
date -u +"START %FT%TZ" >> artifacts/kalmar/logs/$NAME.log
python3 state_ladder_ei.py --init $CK --name $NAME --seed $S --outdir artifacts/kalmar/ladder --ckptdir ckpts/kalmar/ladder \
  --targets data/kalmar/ei_targets1000.jsonl --transfer data/kalmar/ei_transfer200.jsonl \
  --heldout data/kalmar/val300_kal_sl.jsonl --train data/kalmar/train_kal_sl.jsonl \
  --rounds 8 --k 16 --max_action 512 --max_steps 1024 --batch ${LB:-1024} $X "$@" >> artifacts/kalmar/logs/$NAME.log 2>&1
echo "rc=$? END $(date -u +%FT%TZ)" >> artifacts/kalmar/logs/$NAME.log
if [ $ARM = ei ]; then       # does the trained model still follow the algorithm? (greedy reads: batch 1,024)
  F=$(ls ckpts/kalmar/ladder/${NAME}_r*.pt 2>/dev/null | sort -V | tail -n 1)
  if [ -n "$F" ]; then R=$(basename $F .pt)
    python3 kalmar/tf_agree.py --ckpt $F --in data/kalmar/tf1200_kal_sl.jsonl --out artifacts/kalmar/tf/${R}__tf1200.json --batch 1024 > artifacts/kalmar/logs/tf_$R.log 2>&1
    python3 kalmar/kal_free.py --ckpt $F --in data/kalmar/tf1200_kal_sl.jsonl --k 1 --temperature 0 --out artifacts/kalmar/free/${R}__tf1200_greedy.json --max_steps 1024 --max_action 512 --batch 1024 > artifacts/kalmar/logs/fg_$R.log 2>&1
    up artifacts/kalmar/tf; up artifacts/kalmar/free
  fi
fi
up artifacts/kalmar/ladder; up artifacts/kalmar/logs
touch artifacts/kalmar/markers/$NAME.done
