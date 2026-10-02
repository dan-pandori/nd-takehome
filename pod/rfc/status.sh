#!/usr/bin/env bash
# VPS: one line per rfc pod: ladder rounds done / last event, control rounds, GPU memory.  Usage: pod/rfc/status.sh [wait_secs]
[ -n "$1" ] && TO=$(( $1 + 30 )) pod/rfc/sh.sh rfc-p1 "sleep $1" >/dev/null 2>&1
for f in $(ls ~/.config/nd-rl/pods/ | grep '^rfc-' | sort -V); do
  TO=25 pod/rfc/sh.sh $f "echo \"$f \$(nvidia-smi --query-gpu=memory.used --format=csv,noheader | tr -d ' ') | \$(for l in artifacts/rfc/logs/L_*.log; do [ -f \$l ] && echo -n \"\$(basename \$l .log): \$(grep -a '=== round\|STOP\|ladder done\|failure\|Error' \$l | tail -n 1 | cut -c1-60); \"; done) \$(for d in artifacts/rfc/rc_*; do [ -d \$d ] && echo -n \"\$(basename \$d) r\$(ls \$d | grep -c round_); \"; done) \$(ls artifacts/rfc/*.done artifacts/rfc/*.fail 2>/dev/null | xargs -n1 basename 2>/dev/null | tr '\n' ' ')\"" 2>/dev/null || echo "$f unreachable"
done
