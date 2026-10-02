#!/usr/bin/env bash
# Replay-only control from one start (rfc_replay.py).  Usage: bash pod/rfc/control.sh <seed> <start>
source pod/rfc/env.sh; source pod/rfc/ckpt.sh
S=$1; P=$2; N=rc_best12_s${S}_$P; CK=$(startck $S $P)
fetch trajectory/$CK $CK
last=$(ls artifacts/rfc/$N/round_*.json 2>/dev/null | sed 's/.*round_\([0-9]*\).json/\1/' | sort -n | tail -n1)
ND_ARM=RC_$P ND_SEED=$S python3 rfc_replay.py --init $CK --name $N --seed $S --train data/kh/train_k12.jsonl \
  --outdir artifacts/rfc --ckptdir ckpts/rfc/control --start_round $(( ${last:-0} + 1 )) || exit 1
up artifacts/rfc
echo "=== control done $N $(date -u +%FT%TZ)"
