#!/usr/bin/env bash
# Launch a queue script detached on the pod. Usage: pod/sedl/bg.sh <pod> <script relpath> [args]  (no quotes needed)
. ~/.config/nd-rl/env; N=$1; shift; F=~/.config/nd-rl/pods/$N; [ -f "$F" ] || { echo "no pod $N"; exit 1; }; . "$F" 2>/dev/null
S=$1; shift; B=$(basename $S .sh)
timeout 30 ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o BatchMode=yes -o LogLevel=ERROR -o ConnectTimeout=15 -p $POD_PORT root@$POD_IP \
  "cd /workspace/nd-takehome && mkdir -p artifacts/style_edl/logs && setsid nohup bash $S $* > artifacts/style_edl/logs/queue_$B.log 2>&1 < /dev/null & disown; echo launched $S"
