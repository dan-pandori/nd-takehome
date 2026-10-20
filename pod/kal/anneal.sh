#!/usr/bin/env bash
# Addendum 3 (exploratory): replay-only low-LR fine-tune of KAL-D s<S> (the ladder's fine-tune without EI proofs), then
# greedy reads.  Usage: bash pod/kal/anneal.sh <seed> [ei]   ("ei": also read the EI round-1 checkpoint and sample targets)
. pod/kal/env.sh
S=$1; L=artifacts/kalmar/logs; M=artifacts/kalmar/markers
C=ckpts/kalmar/stage1_kalD_s$S.pt; A=ckpts/kalmar/anneal/kalDA_s$S.pt
mkdir -p ckpts/kalmar/anneal ckpts/kalmar/ladder
until [ -s $C ]; do hf buckets cp $BK/kalmar-pretrain/$C $C > /dev/null 2>&1 || sleep 60; done
[ -s data/kalmar/replay20k_s$S.jsonl ] || python3 kalmar/make_replay.py $S > $L/replay_s$S.log 2>&1
if [ ! -s $A ]; then
  date -u +"START %FT%TZ" > $L/anneal_s$S.log
  python3 state_train.py --data data/kalmar/replay20k_s$S.jsonl --init $C --steps 600 --lr 0.0003 --min_lr 3e-05 \
    --warmup 50 --cap 0 --out $A --seed $S --log_every 200 --recs 128 >> $L/anneal_s$S.log 2>&1 \
  || { echo "retry with --max_tokens 100000" >> $L/anneal_s$S.log;
       python3 state_train.py --data data/kalmar/replay20k_s$S.jsonl --init $C --steps 600 --lr 0.0003 --min_lr 3e-05 \
         --warmup 50 --cap 0 --out $A --seed $S --log_every 200 --recs 128 --max_tokens 100000 >> $L/anneal_s$S.log 2>&1; }
  date -u +"END %FT%TZ" >> $L/anneal_s$S.log
fi
reads() {   # tag ckpt
  local T=$1 K=$2
  [ -f $M/tf_$T.done ] || { python3 kalmar/tf_agree.py --ckpt $K --in data/kalmar/tf1200_kal_sl.jsonl --out artifacts/kalmar/tf/${T}__tf1200.json --batch 1024 > $L/tf_$T.log 2>&1 && touch $M/tf_$T.done; }
  [ -f $M/fg_$T.done ] || { python3 kalmar/kal_free.py --ckpt $K --in data/kalmar/tf1200_kal_sl.jsonl --k 1 --temperature 0 --out artifacts/kalmar/free/${T}__tf1200_greedy.json --max_steps 1024 --max_action 512 --batch 1024 > $L/fg_$T.log 2>&1 && touch $M/fg_$T.done; }
  [ -f $M/fv_$T.done ] || { python3 kalmar/kal_free.py --ckpt $K --in data/kalmar/val300_kal_sl.jsonl --k 1 --temperature 0 --out artifacts/kalmar/free/${T}__val300_greedy.json --max_steps 1024 --max_action 512 --batch 1024 > $L/fv_$T.log 2>&1 && touch $M/fv_$T.done; }
}
reads kalDA_s$S $A
if [ "$2" = ei ]; then
  R=ckpts/kalmar/ladder/la_kal_ei_s0_r1.pt
  until [ -s $R ]; do hf buckets cp $BK/kalmar-pretrain/$R $R > /dev/null 2>&1 || sleep 60; done
  reads la_kal_ei_s0_r1 $R
  for T in kalDA_s0:$A kalD_s0:$C; do   # one ladder-style targets sampling: k 16, T 0.8 (seed 2 = the ladder's round-2 seed)
    N=${T%%:*}; K=${T#*:}
    [ -f $M/tgt_$N.done ] || { python3 guided_eval.py --ckpt $K --arm plain --k 16 --seed 2 --sets data/kalmar/ei_targets1000.jsonl --out artifacts/kalmar/eval/${N}_targets_k16 --max_steps 1024 --max_action 512 --batch 1024 > $L/tgt_$N.log 2>&1 && touch $M/tgt_$N.done; }
  done
fi
up artifacts/kalmar/tf; up artifacts/kalmar/free; up artifacts/kalmar/eval; up artifacts/kalmar/logs
touch $M/anneal_s$S.done
