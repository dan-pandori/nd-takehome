#!/usr/bin/env bash
# One pod job: pod/sedl/job.sh <name> <command...>; skips if its log exists (restartable); log + .done in artifacts/style_edl/logs
. pod/sedl/env.sh
N=$1; shift
L=artifacts/style_edl/logs/$N.log
[ -e "$L" ] && { echo "skip $N (log exists)"; exit 0; }
{ echo "START $(date -u +%FT%TZ) $N: $*"; nvidia-smi --query-gpu=name --format=csv,noheader; "$@"; echo "RC $? END $(date -u +%FT%TZ)"; } > "$L" 2>&1
touch artifacts/style_edl/logs/$N.done
