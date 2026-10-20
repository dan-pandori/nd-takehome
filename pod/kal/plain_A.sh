#!/usr/bin/env bash
# Exploratory (Addendum 3): plain k 32 reads of the annealed models, batch 1,024 (KAL-D's sampled-read protocol).
# Usage: bash pod/kal/plain_A.sh <seed> ...   (waits for each model's greedy suite; fetches the ckpt if absent)
cd /workspace/nd-takehome; . pod/kal/env.sh
M=artifacts/kalmar/markers; L=artifacts/kalmar/logs; K=data/kalmar; mkdir -p $M
SETS=data/bs/holdout250.jsonl,data/ladder/transfer_long_rr600.jsonl,data/ladder/transfer_long_ge17.jsonl,data/ladder/transfer_long2.jsonl,data/gt/candidate_v0.jsonl,data/gt/candidate_v1.jsonl,data/gt/batch3.jsonl,data/gt/hand_proved_14.jsonl,data/bs/textbook72.jsonl,$K/g1_premises.jsonl,$K/g2_large.jsonl,$K/g3_classical.jsonl
for S in "$@"; do
  C=ckpts/kalmar/anneal/kalDA_s$S.pt; T=kalDA_s$S
  until [ -s $C ]; do hf buckets cp $BK/kalmar-pretrain/$C $C > /dev/null 2>&1 || sleep 60; done
  [ -f $M/plain32_$T.done ] || { python3 guided_eval.py --ckpt $C --arm plain --k 32 --seed 1 --sets $SETS --out artifacts/kalmar/eval/${T}_plain_k32 --max_steps 1024 --max_action 512 --batch 1024 > $L/plain32_$T.log 2>&1 && touch $M/plain32_$T.done; }
  up artifacts/kalmar/eval; up artifacts/kalmar/logs
done
touch $M/plain_A_$(echo "$@" | tr ' ' '_').done
