#!/usr/bin/env bash
# SN-cap12 Stage-1, the identical recipe to state-cap12's sn_seed.sh (seeds 4, 5). Usage: bash pod/fsup/stage1.sh <seed>
source pod/fsup/env.sh
S=$1; CK=ckpts/fsup/stage1_SN12_s$S.pt
if [ ! -s $CK ]; then
  echo "=== stage1 s$S $(date -u +%FT%TZ)"
  ND_ARM=SN12 ND_SEED=$S python3 state_train.py --data data/kh/train_k12.jsonl --heldout data/p2/heldout.jsonl --mode lean_staten \
    --steps 6000 --recs 128 --cap 12 --seed $S --out $CK || exit 1
fi
up ckpts/fsup
if [ ! -s artifacts/fsup/heldout_SN12_s$S.json ]; then
  python3 state_eval.py --ckpt $CK --in data/p2/heldout.jsonl --k 1 --temperature 0 --batch 2048 \
    --out artifacts/fsup/heldout_SN12_s$S.jsonl --summary artifacts/fsup/heldout_SN12_s$S.json
  up artifacts/fsup
fi
echo "=== stage1 done $(date -u +%FT%TZ)"
