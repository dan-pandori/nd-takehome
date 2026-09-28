#!/usr/bin/env bash
# Stage 1 of one state arm+seed (same command as state-env), then held-out greedy in the environment.
# Usage: bash pod/sf/stage1.sh <S|SN> <seed>
source pod/sf/env.sh
A=$1; S=$2; M=lean_state; [ "$A" = SN ] && M=lean_staten
CK=ckpts/sf2/stage1_${A}_s${S}.pt
echo "=== stage1 ${A} s${S} $(date -u +%FT%TZ)"
python3 state_train.py --data data/p2/train_depth3_f0_a1.jsonl --heldout data/p2/heldout.jsonl \
  --mode $M --steps 6000 --recs 128 --out $CK --cap 6 --seed $S || exit 1
up ckpts/sf2
echo "=== heldout ${A} s${S} $(date -u +%FT%TZ)"
python3 state_eval.py --ckpt $CK --in data/p2/heldout.jsonl --k 1 --temperature 0 --batch 2048 \
  --out artifacts/sf2/heldout_${A}_s${S}.jsonl --summary artifacts/sf2/heldout_${A}_s${S}.json || exit 1
up artifacts/sf2
echo "=== done $(date -u +%FT%TZ)"
