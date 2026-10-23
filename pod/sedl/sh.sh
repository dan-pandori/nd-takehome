#!/usr/bin/env bash
# Run a command in the pod's repo dir. Usage: pod/sedl/sh.sh <pod> "<cmd>"
. ~/.config/nd-rl/env; N=$1; shift; F=~/.config/nd-rl/pods/$N; [ -f "$F" ] || { echo "no pod $N"; exit 1; }; . "$F" 2>/dev/null
exec ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o BatchMode=yes -o LogLevel=ERROR -o ConnectTimeout=15 -o ServerAliveInterval=30 -p $POD_PORT root@$POD_IP "cd /workspace/nd-takehome && $*"
