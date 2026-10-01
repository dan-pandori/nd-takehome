#!/usr/bin/env bash
# Wait for seed S's final Stage-1 checkpoint in the bucket (written by tj-p0), fetch it, run the T1 ladder (pod/tj/seed.sh's
# ladder block, unchanged).  Usage: bash pod/tj/ladder.sh <seed>
source pod/tj/env.sh
S=$1; CK=ckpts/tj/stage1_best12_s${S}_b1200.pt
until [ -s $CK ]; do hf buckets cp $BK/trajectory/$CK $CK.part >/dev/null 2>&1 && mv $CK.part $CK || { rm -f $CK.part; sleep 60; }; done
echo "=== fetched $CK $(date -u +%FT%TZ) md5 $(md5sum < $CK | cut -c1-8)"
export LADDER_ONLY=1   # held-out greedy is read on tj-p0
bash pod/tj/seed.sh $S
