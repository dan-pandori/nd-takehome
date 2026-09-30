#!/usr/bin/env bash
# One best-recipe Stage-1 model + held-out greedy.  Usage: bash pod/bs/stage1.sh <cap 6|12> <seed> <budget_secs>
source pod/bs/env.sh
C=$1; S=$2; BU=$3; B=${B:-2048}
D=$([ "$C" = 6 ] && echo data/p2/train_depth3_f0_a1.jsonl || echo data/kh/train_k12.jsonl)
N=best${C}_s${S}_b${BU}; CK=ckpts/bs/stage1_$N.pt
if [ ! -s $CK ]; then
  echo "=== stage1 $N $(date -u +%FT%TZ)"
  ND_ARM=best$C ND_SEED=$S python3 state_train.py --recipe best --data $D --heldout data/p2/heldout.jsonl --mode lean_staten \
    --cap $C --seed $S --budget_secs $BU --out $CK || exit 1
fi
if [ ! -s artifacts/bs/eval/heldout_$N.json ]; then
  echo "=== heldout $N $(date -u +%FT%TZ)"
  ND_ARM=best$C ND_SEED=$S python3 state_eval.py --ckpt $CK --in data/p2/heldout.jsonl --k 1 --temperature 0 --batch $B \
    --out artifacts/bs/eval/heldout_$N.jsonl --summary artifacts/bs/eval/heldout_$N.json || exit 1
fi
up artifacts/bs; echo "=== done $N $(date -u +%FT%TZ)"
