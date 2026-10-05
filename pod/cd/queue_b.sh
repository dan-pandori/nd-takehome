#!/usr/bin/env bash
# pod B: J2 stage A (all seeds) -> J3 s2
. pod/cd/env.sh
for S in 0 1 2; do bash pod/cd/j2.sh $S > artifacts/cd/logs/j2_s$S.log 2>&1; done
bash pod/cd/j3.sh 2 > artifacts/cd/logs/j3_s2.log 2>&1
echo "$(date -u +%FT%TZ) QUEUE_B_DONE"
