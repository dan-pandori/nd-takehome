#!/usr/bin/env bash
# S1: one SN model on all 383 theorems, k 10,000, stop 50, T 0.8.  $1 = base|ei, $2 = seed, $3 = batch
M=$1; S=$2; B=${3:-4096}
if [ $M = base ]; then CK=ckpts/se/stage1_SN_s$S.pt; else CK=ckpts/se/ladder/la_T1_SN_s${S}_r8.pt; fi
LEAN_GATE_DUMP=artifacts/ss/dump/S1_${M}_T08_s$S.jsonl LEAN_GATE_LOG=artifacts/ss/logs/gate_S1_${M}_T08_s$S.jsonl \
python3 ss_support.py --ckpt $CK --model $M --stage s1 --in data/sc/theorems.jsonl --k 10000 --stop_at 50 \
  --temperature 0.8 --seed $((S * 10 + 5)) --model_seed $S --batch $B --out artifacts/ss/S1_${M}_T08_s$S
