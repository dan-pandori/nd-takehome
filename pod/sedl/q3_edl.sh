#!/usr/bin/env bash
# Phase 4 (style-edl): A_ES (primary; theta* of order 0 saved) and A_fixed E = 4 (chosen on the S_own pilot) for every
# learner seed x stream; lr grid 1e-5,1e-4,1e-3; orders 0,1. Kalmar streams last. Restartable.
. pod/sedl/env.sh
J=pod/sedl/job.sh; D=data/style_edl/streams; O=artifacts/style_edl/edl
for S in S_own S_own2 S_seed S_short S_RL S_Kal; do
  for s in 0 1 2; do
    L=ckpts/bs/stage1_best12_s${s}_b1200.pt
    A="--ckpt $L --stream $D/s$s/$S.stream.jsonl --test $D/s$s/$S.test.jsonl --lrs 1e-5,1e-4,1e-3 --orders 0,1 --arm $S --lseed $s"
    $J edl_s${s}_$S python3 style_edl/edl_run.py $A --algo es --save_theta ckpts/style_edl/s$s/$S --out $O/s$s/$S.json
    $J edlfix_s${s}_$S python3 style_edl/edl_run.py $A --algo fixed --epochs 4 --out $O/s$s/$S.fixed.json
  done
  up artifacts/style_edl/edl
done
up artifacts/style_edl/edl
echo "QUEUE DONE $(date -u +%FT%TZ)"
