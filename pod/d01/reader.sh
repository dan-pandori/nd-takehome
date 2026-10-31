#!/usr/bin/env bash
# The reads of one 0.1 % seed, each waiting for its checkpoint (never during Stage 1, which is time-budgeted): the base's
# plain (x0) and guided (g0) reads beside the ladder, as the 1 % arm had; after the ladder the r16 plain read (x0), and the
# r16 guided read only if artifacts/coe/markers/allow_r16g0 exists by then (budget).  Usage: bash pod/d01/reader.sh <seed>
source pod/d01/env.sh
ARM=dose01; S=$1; N=${ARM}_s${S}; CK=ckpts/coe/stage1_$N.pt
waitf() { until [ -e "$1" ]; do sleep 60; done; }
waitf artifacts/coe/markers/heldout_$N.done
bash pod/d01/read.sh $CK pend_${N}_x0 plain 0
bash pod/d01/read.sh $CK pend_${N}_g0 guided 0
waitf artifacts/coe/markers/ladder_$N.done
bash pod/d01/read.sh ckpts/coe/ladder/la_${N}_r16.pt r16_${N}_x0 plain 0
[ -e artifacts/coe/markers/allow_r16g0 ] && bash pod/d01/read.sh ckpts/coe/ladder/la_${N}_r16.pt r16_${N}_g0 guided 0
touch artifacts/coe/markers/reads_$N.done
echo "=== reads done $N $(date -u +%FT%TZ)"
