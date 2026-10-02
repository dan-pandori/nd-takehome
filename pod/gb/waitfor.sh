#!/usr/bin/env bash
# Block until something changes worth acting on (a new failure, a pair/rerun finishing, N more reads done) or T seconds pass.
# Usage: bash pod/gb/waitfor.sh <seconds>
T=$1; end=$(( $(date +%s) + T ))
state() { for p in gb-p0 gb-p1 gb-p2 gb-p3 gb-p4 gb-p5; do podrun $p "cd /workspace/nd-takehome; ls artifacts/gb/*.done artifacts/gb/*.fail 2>/dev/null; grep -l -E 'Traceback|READ FAILED' artifacts/gb/logs/*.log 2>/dev/null" 2>/dev/null; done | sort | md5sum; }
s0=$(state)
while [ $(date +%s) -lt $end ]; do
  sleep 60
  [ "$(state)" != "$s0" ] && { echo "CHANGED $(date -u +%T)"; exit 0; }
done
echo "timeout $(date -u +%T)"
