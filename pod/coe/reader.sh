#!/usr/bin/env bash
# The reads of one seed, in order, each waiting for its checkpoint.  Never runs during Stage 1 (time-budgeted).
# Usage: bash pod/coe/reader.sh <full|ko> <seed>
source pod/coe/env.sh
ARM=$1; S=$2; N=${ARM}_s${S}; CK=ckpts/coe/stage1_$N.pt; L=artifacts/coe/ladder/la_$N
waitf() { until [ -e "$1" ]; do sleep 60; done; }
waitf artifacts/coe/markers/heldout_$N.done
bash pod/coe/read.sh $CK pend_${N}_x0 plain 0
bash pod/coe/read.sh $CK pend_${N}_g0 guided 0
bash pod/coe/read.sh $CK pend_${N}_x1 plain 1
waitf $L/round_8.json
bash pod/coe/read.sh ckpts/coe/ladder/la_${N}_r8.pt r8_${N}_x0 plain 0
waitf artifacts/coe/markers/ladder_$N.done
bash pod/coe/read.sh ckpts/coe/ladder/la_${N}_r16.pt r16_${N}_x0 plain 0
bash pod/coe/read.sh ckpts/coe/ladder/la_${N}_r16.pt r16_${N}_g0 guided 0
bash pod/coe/read.sh ckpts/coe/ladder/la_${N}_r16.pt r16_${N}_x1 plain 1
touch artifacts/coe/markers/reads_$N.done
echo "=== reads done $N $(date -u +%FT%TZ)"
