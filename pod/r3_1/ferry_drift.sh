#!/usr/bin/env bash
# Pull every drift-arm checkpoint (r2/r4/r6/r8) that exists on the source pod and push it to the target pod.
# Usage: bash pod/r3_1/ferry_drift.sh <src> <dst> <pattern>
SRC=$1; DST=$2; PAT=$3; R=/home/dan/work/round3-run1; cd $R
for f in $(podrun $SRC "ls ckpts/r3_1 | grep -E '^ei_${PAT}_s[0-9]+_drift_r(2|4|6|8)\.pt$'"); do
  [ -f ckpts/r3_1/$f ] || bash pod/r3_1/wpod.sh pull $SRC ckpts/r3_1/$f
  bash pod/r3_1/wpod.sh push $DST ckpts/r3_1/$f
done
podrun $DST "ls ckpts/r3_1 | grep drift | tr '\n' ' '"
