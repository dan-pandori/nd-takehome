#!/usr/bin/env bash
# One ladder (state-cap12's SN protocol: 8 rounds, k 32, T 0.8, batch 2048, replay K12) + its read-out.
# Usage: bash pod/fsup/ladder.sh <arm C|S|R> <seed> [extra args]   C control, S supply (25 %), R control rerun (EI seed + 100)
source pod/fsup/env.sh
A=$1; S=$2; shift 2; N=la_${A}_s$S
CK=ckpts/sc12/stage1_SN12_s$S.pt; [ -s $CK ] || CK=ckpts/fsup/stage1_SN12_s$S.pt
[ -s $CK ] || { echo "waiting for $CK in the bucket $(date -u +%FT%TZ)"; until [ -s $CK ]; do hf buckets cp $BK/$CK $CK >/dev/null 2>&1 || sleep 120; done; }
case $A in C) X="";; S) X="--supply_frac 0.25";; R) X="--ei_seed $((S+100))";; *) echo "bad arm"; exit 1;; esac
if [ ! -s ckpts/fsup/ladder/${N}_r8.pt ]; then
  echo "=== ladder $N $(date -u +%FT%TZ) init $CK"
  ND_ARM=$N ND_SEED=$S python3 state_ladder_ei.py --init $CK --name $N --seed $S --batch 2048 --transfer_k 0 $X "$@" \
    --train data/kh/train_k12.jsonl --heldout data/p2/heldout.jsonl --outdir artifacts/fsup --ckptdir ckpts/fsup/ladder || exit 1
  up artifacts/fsup/$N; up ckpts/fsup
fi
bash pod/fsup/reread.sh ckpts/fsup/ladder/${N}_r8.pt $N
echo "=== ladder done $(date -u +%FT%TZ)"
