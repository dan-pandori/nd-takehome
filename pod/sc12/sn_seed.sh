#!/usr/bin/env bash
# One seed of SN-cap12: Stage-1 on K12 (lean_staten, cap 12), held-out greedy, ladder T1, long-pool / original-pool re-reads.
# Usage: bash pod/sc12/sn_seed.sh <seed>
source pod/sc12/env.sh
S=$1; B=2048; CK=ckpts/sc12/stage1_SN12_s$S.pt
if [ ! -s $CK ]; then
  echo "=== stage1 s$S $(date -u +%FT%TZ)"
  ND_ARM=SN12 ND_SEED=$S python3 state_train.py --data data/kh/train_k12.jsonl --heldout data/p2/heldout.jsonl --mode lean_staten \
    --steps 6000 --recs 128 --cap 12 --seed $S --out $CK || exit 1
fi
up ckpts/sc12
if [ ! -s artifacts/sc12/heldout_SN12_s$S.json ]; then
  echo "=== heldout s$S $(date -u +%FT%TZ)"
  python3 state_eval.py --ckpt $CK --in data/p2/heldout.jsonl --k 1 --temperature 0 --batch $B \
    --out artifacts/sc12/heldout_SN12_s$S.jsonl --summary artifacts/sc12/heldout_SN12_s$S.json
  up artifacts/sc12
fi
[ -f artifacts/sc12/GATES_OK ] || { echo "waiting for GATES_OK $(date -u +%FT%TZ)"; until [ -f artifacts/sc12/GATES_OK ]; do sleep 30; done; }
if [ ! -s ckpts/sc12/ladder/la_T1_SN12_s${S}_r8.pt ]; then
  echo "=== ladder T1 s$S $(date -u +%FT%TZ)"
  ND_ARM=SN12 ND_SEED=$S LEAN_GATE_DUMP=artifacts/sc12/dump/la_T1_SN12_s$S.jsonl python3 state_ladder_ei.py --init $CK --name la_T1_SN12_s$S \
    --seed $S --batch $B --train data/kh/train_k12.jsonl --heldout data/p2/heldout.jsonl --outdir artifacts/sc12 --ckptdir ckpts/sc12/ladder || exit 1
  up artifacts/sc12; up ckpts/sc12
fi
bash pod/sc12/reread.sh ckpts/sc12/ladder/la_T1_SN12_s${S}_r8.pt T1_SN12_s$S
bash pod/sc12/reread.sh $CK stage1_SN12_s$S orig
echo "=== seed done $(date -u +%FT%TZ)"
