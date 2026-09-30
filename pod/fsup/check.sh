#!/usr/bin/env bash
# One line per ladder: latest round and supply summary; per pod: GPU memory, load.  Usage: pod/fsup/check.sh [pods...]
. ~/.config/nd-rl/env
for N in ${@:-fsup1 fsup2 fsup3 fsup4}; do F=~/.config/nd-rl/pods/$N; [ -f "$F" ] || continue; . "$F"
  timeout 60 ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o BatchMode=yes -o LogLevel=ERROR -p $POD_PORT root@$POD_IP \
   "cd /workspace/nd-takehome; echo \"## $N \$(nvidia-smi --query-gpu=memory.used,utilization.gpu --format=csv,noheader) load \$(cut -d' ' -f1 /proc/loadavg)\"; ls artifacts/fsup/*.done artifacts/fsup/*.fail 2>/dev/null | xargs -n1 basename 2>/dev/null | tr '\n' ' '; echo; for l in artifacts/fsup/logs/la_*.log; do echo \"\$(basename \$l .log): \$(grep -a '=== round\|supply r' \$l | tail -2 | cut -c1-170 | tr '\n' '|')\"; done; grep -ah 'FAIL\|Error\|Traceback' artifacts/fsup/logs/*.log | head -3"
done
