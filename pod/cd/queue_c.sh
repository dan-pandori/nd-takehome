#!/usr/bin/env bash
# pod C: J5 missing plain draws -> J3 cap 6 (all seeds)
. pod/cd/env.sh
bash pod/cd/j5.sh > artifacts/cd/logs/j5.log 2>&1
for S in 0 1 2; do bash pod/cd/j3c6.sh $S > artifacts/cd/logs/j3c6_s$S.log 2>&1; done
echo "$(date -u +%FT%TZ) QUEUE_C_DONE"
