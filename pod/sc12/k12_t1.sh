#!/usr/bin/env bash
# Comparator: cap-horizon's K12 whole-proof Stage-1 -> ladder T1 (8 x 32) under Lean alone, then the long-pool re-read.
# Usage: bash pod/sc12/k12_t1.sh <seed>
source pod/sc12/env.sh
S=$1; CK=ckpts/kh/stage1_k12_s$S.pt
if [ ! -s ckpts/ladder/la_T1_K12_s${S}_r8.pt ]; then
  echo "=== ladder T1 K12 s$S $(date -u +%FT%TZ)"
  ND_ARM=K12 ND_SEED=$S LEAN_GATE_DUMP=artifacts/sc12/dump/la_T1_K12_s$S.jsonl python3 ladder_ei.py --init $CK --name la_T1_K12_s$S --seed $S \
    --batch 2048 --max_new 512 --train data/kh/train_k12.jsonl --heldout data/p2/heldout.jsonl --outdir artifacts/sc12 || exit 1
  up artifacts/sc12; up ckpts/ladder
fi
WP=1 bash pod/sc12/reread.sh ckpts/ladder/la_T1_K12_s${S}_r8.pt T1_K12_s$S
echo "=== k12 done $(date -u +%FT%TZ)"
