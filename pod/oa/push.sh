#!/usr/bin/env bash
# Push this worktree's code and data/oa, data/ladder to a pod.  Usage: pod/oa/push.sh <pod>
. ~/.config/nd-rl/env; N=$1; F=~/.config/nd-rl/pods/$N; [ -f "$F" ] || { echo "no pod $N"; exit 1; }; . "$F" 2>/dev/null
SSHO="-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o BatchMode=yes -o LogLevel=ERROR -o ServerAliveInterval=30"
W=/home/dan/work/organism-analysis
rsync -rlptz --no-o --no-g --exclude .git --exclude data/ --exclude artifacts/ --exclude ckpts/ --exclude __pycache__ \
  -e "ssh $SSHO -p $POD_PORT" $W/ "root@$POD_IP:/workspace/nd-takehome/" || exit 1
cd $W && exec rsync -rlptzR --no-o --no-g -e "ssh $SSHO -p $POD_PORT" data/oa data/ladder "root@$POD_IP:/workspace/nd-takehome/"
