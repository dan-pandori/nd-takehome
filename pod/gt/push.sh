#!/usr/bin/env bash
# Push THIS run worktree's code (and data/gt) to a pod. Usage: pod/gt/push.sh <pod>
. ~/.config/nd-rl/env; N=$1; F=~/.config/nd-rl/pods/$N; [ -f "$F" ] || { echo "no pod $N"; exit 1; }; . "$F" 2>/dev/null
SSHO="-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o BatchMode=yes -o LogLevel=ERROR -o ServerAliveInterval=30"
rsync -rlptz --no-o --no-g --exclude .git --exclude data/ --exclude artifacts/ --exclude ckpts/ --exclude __pycache__ \
  -e "ssh $SSHO -p $POD_PORT" /home/dan/work/guided-tts/ "root@$POD_IP:/workspace/nd-takehome/" || exit 1
cd /home/dan/work/guided-tts && exec rsync -rlptzR --no-o --no-g -e "ssh $SSHO -p $POD_PORT" data/gt "root@$POD_IP:/workspace/nd-takehome/"
