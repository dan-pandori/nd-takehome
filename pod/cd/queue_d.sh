#!/usr/bin/env bash
# pod D: J6 (all seeds)
. pod/cd/env.sh
for S in 0 1 2; do bash pod/cd/j6.sh $S > artifacts/cd/logs/j6_s$S.log 2>&1; done
echo "$(date -u +%FT%TZ) QUEUE_D_DONE"
