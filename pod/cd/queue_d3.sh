#!/usr/bin/env bash
# pod D after J6: J6b (all seeds) then J2 stage A' / B (all seeds).
. pod/cd/env.sh
until grep -q QUEUE_D_DONE artifacts/cd/logs/queue_d.log 2>/dev/null; do sleep 60; done
for S in 0 1 2; do bash pod/cd/j6b.sh $S > artifacts/cd/logs/j6b_s$S.log 2>&1; done
for S in 0 1 2; do bash pod/cd/j2b.sh $S > artifacts/cd/logs/j2b_s$S.log 2>&1; done
echo "$(date -u +%FT%TZ) QUEUE_D3_DONE"
