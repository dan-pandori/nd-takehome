#!/usr/bin/env bash
# Run a command in the pod's repo dir.  Usage: pod/cm/sh.sh <pod> "<command>"
. ~/.config/nd-rl/env; N=$1; shift; F=~/.config/nd-rl/pods/$N; [ -f "$F" ] || { echo "no pod $N"; exit 1; }; . "$F" 2>/dev/null
SSHO="-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o BatchMode=yes -o LogLevel=ERROR -o ServerAliveInterval=30 -o ConnectTimeout=20"
exec timeout ${T:-60} ssh $SSHO -p "$POD_PORT" "root@$POD_IP" "cd /workspace/nd-takehome && $*"
