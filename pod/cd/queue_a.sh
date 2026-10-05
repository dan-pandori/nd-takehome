#!/usr/bin/env bash
# pod A: J1 stage 1 (all seeds) -> J4 (all seeds) -> J3 s0, s1
. pod/cd/env.sh
for S in 0 1 2; do bash pod/cd/j1.sh $S 1 > artifacts/cd/logs/j1_s$S.log 2>&1; done
for S in 0 1 2; do bash pod/cd/j4.sh $S > artifacts/cd/logs/j4_s$S.log 2>&1; done
for S in 0 1; do bash pod/cd/j3.sh $S > artifacts/cd/logs/j3_s$S.log 2>&1; done
echo "$(date -u +%FT%TZ) QUEUE_A_DONE"
