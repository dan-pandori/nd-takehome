#!/usr/bin/env bash
# One-line progress per pod: stage lines from chunk logs, done/fail markers, load.
for N in "$@"; do . ~/.config/nd-rl/pods/$N
  timeout 60 ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR -o ConnectTimeout=15 -p $POD_PORT root@$POD_IP \
   "cd /workspace/nd-takehome/artifacts/lpool2; echo == $N \$(date -u +%H:%M) load \$(cut -d' ' -f1 /proc/loadavg); ls *.done *.fail 2>/dev/null | tr '\n' ' '; for f in *.log; do echo \"\$f: \$(grep -E 'GEN_DONE|STAGE_|LABEL_DONE|START' \$f | tail -1 | cut -c12-80)\"; done"
done
