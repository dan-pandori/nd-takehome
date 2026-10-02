#!/usr/bin/env bash
# Run a short command on a pod in /workspace/nd-takehome.  Usage: pod/rfc/sh.sh <pod> "<cmd>"
. ~/.config/nd-rl/env; N=$1; shift; F=~/.config/nd-rl/pods/$N; [ -f "$F" ] || { echo "no pod $N"; exit 1; }; . "$F" 2>/dev/null
timeout ${TO:-60} ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o BatchMode=yes -o LogLevel=ERROR -p "$POD_PORT" "root@$POD_IP" "cd /workspace/nd-takehome && $*"
