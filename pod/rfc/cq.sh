#!/usr/bin/env bash
# Run replay-only controls one after another.  Usage: bash pod/rfc/cq.sh "<seed> <start>" ...
for j in "$@"; do bash pod/rfc/control.sh $j > artifacts/rfc/logs/C_$(echo $j | tr ' ' _).log 2>&1 || echo "CONTROL FAILED $j"; done
echo "=== cq done $(date -u +%FT%TZ)"
