#!/usr/bin/env bash
# VPS: poll the rfc pods every 5 min; exit (printing a short status) on any new *.fail / FAILED / Traceback, or after $1 min.
cd /home/dan/work/rl-from-ckpt; M=${1:-60}; t0=$(date +%s)
seen=/tmp/rfc/watch_seen; touch $seen
while true; do
  bad=""
  for f in $(ls ~/.config/nd-rl/pods/ | grep '^rfc-'); do
    o=$(TO=25 pod/rfc/sh.sh $f "ls artifacts/rfc/*.fail 2>/dev/null; grep -l 'Traceback\|FAILED' artifacts/rfc/logs/*.log 2>/dev/null" </dev/null 2>/dev/null)
    for x in $o; do grep -qx "$f:$x" $seen || { bad="$bad $f:$x"; echo "$f:$x" >> $seen; }; done
  done
  [ -n "$bad" ] && { echo "NEW PROBLEMS:$bad"; break; }
  [ $(( $(date +%s) - t0 )) -ge $(( M * 60 )) ] && break
  sleep 300
done
date -u +%T; pod/rfc/status.sh 2>/dev/null | cut -c1-200
