#!/usr/bin/env bash
# One cm12 seed: the T1 ladder (state-cap12's protocol, only --k raised) from the inherited SN-cap12 Stage-1 checkpoint,
# then the T1 read-outs.  The ladder runs alone on the pod, so its wall-clock is its GPU-seconds.
# Usage: bash pod/cm/seed.sh <seed> <k>
source pod/cm/env.sh
S=$1; K=$2; CK=ckpts/inh/Fz_SN12_s$S.pt; N=la_T1_cm12k${K}_s$S
[ -s $CK ] || hf buckets cp $BK/state-cap12/ckpts/sc12/stage1_SN12_s$S.pt $CK || exit 1
md5sum $CK
if [ ! -s ckpts/cm/ladder/${N}_r8.pt ]; then
  echo "=== ladder $N $(date -u +%FT%TZ)"
  ND_ARM=cm12k$K ND_SEED=$S LEAN_GATE_DUMP=artifacts/cm/dump/$N.jsonl python3 state_ladder_ei.py --init $CK --name $N \
    --seed $S --k $K --batch 2048 --train data/kh/train_k12.jsonl --heldout data/p2/heldout.jsonl --outdir artifacts/cm \
    --ckptdir ckpts/cm/ladder || exit 1
  gzip -f artifacts/cm/dump/$N.jsonl
  up artifacts/cm; up ckpts/cm
  hf buckets sync artifacts/cm/dump $BK/compute-match/artifacts/cm/dump --include '*.gz' >/dev/null 2>&1 || echo "DUMP UPLOAD FAILED"
  echo "=== ladder done $N $(date -u +%FT%TZ)"
fi
ND_ARM=cm12k$K ND_SEED=$S bash pod/cm/read.sh ckpts/cm/ladder/${N}_r8.pt T1_cm12k${K}_s$S tb72 dev held h250 long2 rr600
echo "=== seed done $N $(date -u +%FT%TZ)"
