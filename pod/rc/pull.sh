#!/usr/bin/env bash
# Pull artifacts/rc from a pod into THIS worktree, without the large per-round found/mix files and the eval .jsonl
# (those stay in the bucket).  Usage: pod/rc/pull.sh <pod> [extra rsync args]
. ~/.config/nd-rl/env; N=$1; shift; F=~/.config/nd-rl/pods/$N; [ -f "$F" ] || { echo "no pod $N"; exit 1; }; . "$F" 2>/dev/null
SSHO="-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o BatchMode=yes -o LogLevel=ERROR -o ServerAliveInterval=30"
mkdir -p /home/dan/work/rl-continue/artifacts/rc
exec rsync -rlptz --no-o --no-g --exclude 'found_*' --exclude 'mix_*' --exclude '*.tmp' "$@" \
  -e "ssh $SSHO -p $POD_PORT" "root@$POD_IP:/workspace/nd-takehome/artifacts/rc/" /home/dan/work/rl-continue/artifacts/rc/
