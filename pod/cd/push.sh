#!/usr/bin/env bash
# Push THIS run worktree's code and inputs to a pod. Usage: pod/cd/push.sh <pod> [extra relpath ...]
. ~/.config/nd-rl/env; N=$1; shift; F=~/.config/nd-rl/pods/$N; [ -f "$F" ] || { echo "no pod $N"; exit 1; }; . "$F" 2>/dev/null
SSHO="-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o BatchMode=yes -o LogLevel=ERROR -o ServerAliveInterval=30"
W=/home/dan/work/capability-defs
git -C $W rev-parse HEAD > $W/.git_sha
rsync -rlptz --no-o --no-g --exclude .git --exclude data/ --exclude artifacts/ --exclude ckpts/ --exclude __pycache__ \
  -e "ssh $SSHO -p $POD_PORT" $W/ "root@$POD_IP:/workspace/nd-takehome/" || exit 1
cd $W && exec rsync -rlptzR --no-o --no-g -e "ssh $SSHO -p $POD_PORT" data/cd data/bs data/gt "$@" "root@$POD_IP:/workspace/nd-takehome/"
