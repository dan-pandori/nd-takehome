#!/usr/bin/env bash
# Pull one path from a pod back into THIS run worktree (no ladder found_*.jsonl, no dumps). Usage: pod/gb/pull.sh <pod> <relpath>
. ~/.config/nd-rl/env; N=$1; shift; F=~/.config/nd-rl/pods/$N; [ -f "$F" ] || { echo "no pod $N"; exit 1; }; . "$F" 2>/dev/null
SSHO="-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o BatchMode=yes -o LogLevel=ERROR -o ServerAliveInterval=30"
D=/home/dan/work/grpo-best/$1; mkdir -p "$(dirname "$D")"
exec rsync -rlptz --no-o --no-g --exclude 'dump/' --exclude 'found_*.jsonl' --exclude '*.pt' -e "ssh $SSHO -p $POD_PORT" "root@$POD_IP:/workspace/nd-takehome/$1" "$(dirname "$D")/"
