#!/usr/bin/env bash
# VPS: wait up to $1 minutes (default 9), polling every 3 min; return early when brief.sh reports a NEW marker.
M=${1:-9}; t0=$(date +%s)
while true; do o=$(bash /home/dan/work/rl-from-ckpt/pod/rfc/brief.sh); echo "$o" | grep -q NEW && break
  [ $(( $(date +%s) - t0 + 180 )) -gt $(( M * 60 )) ] && break; sleep 180; done; echo "$o"
