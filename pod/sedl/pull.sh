#!/usr/bin/env bash
# Pull one path from a pod into THIS run worktree. Usage: pod/sedl/pull.sh <pod> <relpath> [extra rsync args]
. ~/.config/nd-rl/env; N=$1; shift; F=~/.config/nd-rl/pods/$N; [ -f "$F" ] || { echo "no pod $N"; exit 1; }; . "$F" 2>/dev/null
SSHO="-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o BatchMode=yes -o LogLevel=ERROR -o ServerAliveInterval=30"
P=$1; shift
D=/home/dan/work/style-edl/$P; mkdir -p "$(dirname "$D")"
exec rsync -rlptz --no-o --no-g "$@" -e "ssh $SSHO -p $POD_PORT" "root@$POD_IP:/workspace/nd-takehome/$P" "$(dirname "$D")/"
