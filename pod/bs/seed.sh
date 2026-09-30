#!/usr/bin/env bash
# One best-recipe cell seed: Stage-1 (1,200 s, the pilot's choice) + held-out greedy, then the T1 ladder
# (state-cap12's protocol: state_ladder_ei.py defaults, 8 rounds x k 32, T 0.8, replay from the cell's own data).
# Usage: bash pod/bs/seed.sh <cap 6|12> <seed>          env LB = ladder sampling batch (default 2048)
source pod/bs/env.sh
C=$1; S=$2; LB=${LB:-2048}; BU=1200
D=$([ "$C" = 6 ] && echo data/p2/train_depth3_f0_a1.jsonl || echo data/kh/train_k12.jsonl)
N=best${C}_s${S}_b${BU}; CK=ckpts/bs/stage1_$N.pt
[ -s $CK ] || hf buckets cp $BK/best-state/$CK $CK >/dev/null 2>&1
bash pod/bs/stage1.sh $C $S $BU || exit 1
up ckpts/bs
if [ ! -s ckpts/bs/ladder/la_T1_best${C}_s${S}_r8.pt ]; then
  echo "=== ladder T1 best$C s$S $(date -u +%FT%TZ)"
  ND_ARM=best$C ND_SEED=$S LEAN_GATE_DUMP=artifacts/bs/dump/la_T1_best${C}_s$S.jsonl python3 state_ladder_ei.py --init $CK \
    --name la_T1_best${C}_s$S --seed $S --batch $LB --train $D --heldout data/p2/heldout.jsonl --outdir artifacts/bs \
    --ckptdir ckpts/bs/ladder || exit 1
  gzip -f artifacts/bs/dump/la_T1_best${C}_s$S.jsonl
  up artifacts/bs; up ckpts/bs
  hf buckets sync artifacts/bs/dump $BK/best-state/artifacts/bs/dump --include '*.gz' >/dev/null 2>&1 || echo "DUMP UPLOAD FAILED"
fi
echo "=== seed done best$C s$S $(date -u +%FT%TZ)"
