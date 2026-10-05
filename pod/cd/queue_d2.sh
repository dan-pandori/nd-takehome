#!/usr/bin/env bash
# pod D, after J6: J2 stage A' (and stage B files present at the time) for all seeds.  Waits for queue D.
. pod/cd/env.sh
until grep -q QUEUE_D_DONE artifacts/cd/logs/queue_d.log 2>/dev/null; do sleep 60; done
for S in 0 1 2; do bash pod/cd/j2b.sh $S > artifacts/cd/logs/j2b_s$S.log 2>&1; done
echo "$(date -u +%FT%TZ) QUEUE_D2_DONE"
