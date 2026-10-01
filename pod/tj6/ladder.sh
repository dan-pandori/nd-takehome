#!/usr/bin/env bash
# Wait for seed S's final Stage-1 checkpoint in the bucket (written by tj-p0), fetch it, run the T1 ladder (pod/tj6/seed.sh's
# ladder block, unchanged).  Usage: bash pod/tj6/ladder.sh <seed>
source pod/tj6/env.sh
S=$1; CK=ckpts/tj6/stage1_best6_s${S}_b1200.pt
until [ -s $CK ]; do hf buckets cp $BK/trajectory-cap6/$CK $CK.part >/dev/null 2>&1 && mv $CK.part $CK || { rm -f $CK.part; sleep 60; }; done
echo "=== fetched $CK $(date -u +%FT%TZ) md5 $(md5sum < $CK | cut -c1-8)"
export LADDER_ONLY=1   # held-out greedy is read on tj-p0
bash pod/tj6/seed.sh $S
