#!/usr/bin/env bash
# One pod job: pod/kc/job.sh <name> <command...>; skips if its log exists (restartable); log + .done in artifacts/kc/logs
. pod/kc/env.sh
N=$1; shift
L=artifacts/kc/logs/$N.log
[ -e "$L" ] && { echo "skip $N (log exists)"; exit 0; }
{ echo "START $(date -u +%FT%TZ) $N: $*"; nvidia-smi --query-gpu=name --format=csv,noheader; "$@"; echo "RC $? END $(date -u +%FT%TZ)"; } > "$L" 2>&1
touch artifacts/kc/logs/$N.done
