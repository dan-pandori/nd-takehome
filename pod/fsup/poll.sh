#!/usr/bin/env bash
# Sleep ~9.5 min, then one compact line per pod: ladders' last completed round and last supply pass count; failures.
sleep ${1:-570}
. ~/.config/nd-rl/env; date -u +%H:%M
for N in fsup6 fsup7 fsup8 fsup9 fsup10; do F=~/.config/nd-rl/pods/$N; [ -f "$F" ] || { echo "$N gone"; continue; }; . "$F"
  timeout 60 ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o BatchMode=yes -o LogLevel=ERROR -p $POD_PORT root@$POD_IP \
   "cd /workspace/nd-takehome; o=\"$N \$(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits)MB\"; for l in artifacts/fsup/logs/la_*.log; do b=\$(basename \$l .log); r=\$(grep -ac '=== round' \$l); p=\$(grep -a 'supply r' \$l | tail -1 | grep -o 'pass [0-9]*'); o=\"\$o | \$b r\$r \$p\"; done; echo \"\$o \$(ls artifacts/fsup/*.fail 2>/dev/null | xargs -rn1 basename | tr '\n' ' ')\"" || echo "$N ssh fail"
done
