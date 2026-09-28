#!/usr/bin/env bash
# One ladder (T1 or frozen) for a Stage-1 checkpoint of this run.  Usage: bash pod/sf/ladder.sh <S|SN> <seed> <T1|frozen>
source pod/sf/env.sh
A=$1; S=$2; K=$3; X=""; [ "$K" = frozen ] && X=--no_train
CK=ckpts/sf2/stage1_${A}_s${S}.pt
[ -f $CK ] || hf buckets cp $BK/$CK $CK
md5sum $CK
echo "=== ladder $K ${A} s${S} $(date -u +%FT%TZ)"
python3 state_ladder_ei.py --init $CK --name la_${K}_${A}_s${S} --seed $S --batch 2048 --outdir artifacts/sf2 --ckptdir ckpts/sf2/ladder \
  --train data/p2/train_depth3_f0_a1.jsonl --heldout data/p2/heldout.jsonl $X || exit 1
up artifacts/sf2; up ckpts/sf2
echo "=== done $(date -u +%FT%TZ)"
