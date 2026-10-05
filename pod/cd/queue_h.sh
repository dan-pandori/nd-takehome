#!/usr/bin/env bash
. pod/cd/env.sh
for S in 0 1 2; do bash pod/cd/j8.sh $S > artifacts/cd/logs/j8_s$S.log 2>&1; done
echo "$(date -u +%FT%TZ) QUEUE_H_DONE"
