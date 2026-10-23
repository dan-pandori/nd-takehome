#!/usr/bin/env bash
# Phase 4 on sedl2 (style-edl): the Kalmar cells of seeds 1 and 2 (A_ES with theta* saved, A_fixed E = 4), then their
# cross-fit (exploratory). Same commands as q3_edl.sh / q3x_xfit.sh. Restartable.
. pod/sedl/env.sh
J=pod/sedl/job.sh; D=data/style_edl/streams; O=artifacts/style_edl/edl; S=S_Kal
for s in 1 2; do
  L=ckpts/bs/stage1_best12_s${s}_b1200.pt
  A="--ckpt $L --stream $D/s$s/$S.stream.jsonl --test $D/s$s/$S.test.jsonl --lrs 1e-5,1e-4,1e-3 --orders 0,1 --arm $S --lseed $s"
  $J edl_s${s}_$S python3 style_edl/edl_run.py $A --algo es --save_theta ckpts/style_edl/s$s/$S --out $O/s$s/$S.json
  $J edlfix_s${s}_$S python3 style_edl/edl_run.py $A --algo fixed --epochs 4 --out $O/s$s/$S.fixed.json
  up artifacts/style_edl/edl
done
for s in 1 2; do
  L=ckpts/bs/stage1_best12_s${s}_b1200.pt
  $J xfit_s${s}_$S python3 style_edl/edl_run.py --ckpt $L --stream $D/s$s/$S.test.jsonl --test $D/s$s/$S.stream.jsonl --lrs 1e-5,1e-4,1e-3 --orders 0,1 --arm $S --lseed $s --algo es --out artifacts/style_edl/edl_x/s$s/$S.json
done
up artifacts/style_edl/edl_x
echo "QUEUE DONE $(date -u +%FT%TZ)"
