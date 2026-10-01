#!/usr/bin/env bash
# One best-cap12 seed with kept checkpoints: Stage-1 (1,200 s, best-state's flags + --save_steps) + held-out greedy,
# then the T1 ladder exactly as pod/bs/seed.sh (8 rounds x k 32, T 0.8, replay from K12, ladder batch 2,048).
# Usage: bash pod/tj/seed.sh <seed>
source pod/tj/env.sh
S=$1; LB=${LB:-2048}; BU=1200; D=data/kh/train_k12.jsonl
SAVE=${SAVE:-0,50,100,200,400,800,1600,3000,5000,8000,12000,16000,20000}
N=best12_s${S}_b${BU}; CK=ckpts/tj/stage1_$N.pt
if [ ! -s $CK ]; then
  echo "=== stage1 $N $(date -u +%FT%TZ)"
  ND_ARM=best12 ND_SEED=$S python3 state_train.py --recipe best --data $D --heldout data/p2/heldout.jsonl --mode lean_staten \
    --cap 12 --seed $S --budget_secs $BU --save_steps $SAVE --out $CK || exit 1
fi
if [ "${LADDER_ONLY:-0}" != 1 ] && [ ! -s artifacts/tj/eval/heldout_$N.json ]; then
  echo "=== heldout $N $(date -u +%FT%TZ)"
  ND_ARM=best12 ND_SEED=$S python3 state_eval.py --ckpt $CK --in data/p2/heldout.jsonl --k 1 --temperature 0 --batch 2048 \
    --out artifacts/tj/eval/heldout_$N.jsonl --summary artifacts/tj/eval/heldout_$N.json || exit 1
fi
up artifacts/tj
[ "${STAGE1_ONLY:-0}" = 1 ] && { echo "=== stage1 only, done $N $(date -u +%FT%TZ)"; exit 0; }
if [ ! -s ckpts/tj/ladder/la_T1_best12_s${S}_r8.pt ]; then
  echo "=== ladder T1 best12 s$S $(date -u +%FT%TZ)"
  ND_ARM=best12 ND_SEED=$S python3 state_ladder_ei.py --init $CK \
    --name la_T1_best12_s$S --seed $S --batch $LB --train $D --heldout data/p2/heldout.jsonl --outdir artifacts/tj \
    --ckptdir ckpts/tj/ladder || exit 1
  up artifacts/tj
fi
echo "=== seed done best12 s$S $(date -u +%FT%TZ)"
