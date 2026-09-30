#!/usr/bin/env bash
# Pull artifacts/sx from a pod into this worktree without the Lean dumps and fine-tune mixes. Usage: pod/sx/pullsmall.sh <pod> [--with-found]
. ~/.config/nd-rl/env; N=$1; F=~/.config/nd-rl/pods/$N; [ -f "$F" ] || { echo "no pod $N"; exit 1; }; . "$F"
SSHO="-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o BatchMode=yes -o LogLevel=ERROR -o ServerAliveInterval=30"
EX="--exclude dump/ --exclude mix_*.jsonl"; [ "$2" = --with-found ] || EX="$EX --exclude found_*.jsonl"
exec rsync -rlptz --no-o --no-g $EX -e "ssh $SSHO -p $POD_PORT" "root@$POD_IP:/workspace/nd-takehome/artifacts/sx/" /home/dan/work/search-expert/artifacts/sx/
