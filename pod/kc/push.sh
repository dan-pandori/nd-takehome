#!/usr/bin/env bash
# Push THIS run worktree's code (+ the small data it needs) to a pod. Usage: pod/kc/push.sh <pod>
. ~/.config/nd-rl/env; N=$1; F=~/.config/nd-rl/pods/$N; [ -f "$F" ] || { echo "no pod $N"; exit 1; }; . "$F" 2>/dev/null
W=/home/dan/work/kalmar-complexity
git -C $W rev-parse HEAD > $W/pod/kc/GIT_SHA
SSHO="-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o BatchMode=yes -o LogLevel=ERROR -o ServerAliveInterval=30"
rsync -rlptz --no-o --no-g --exclude .git --exclude data/ --exclude artifacts/ --exclude ckpts/ --exclude __pycache__ \
  --exclude 'review_*' --exclude '.venv*' --exclude 'logs_kc' --exclude 'kalmar_complexity/tok' \
  -e "ssh $SSHO -p $POD_PORT" $W/ "root@$POD_IP:/workspace/nd-takehome/" || exit 1
cd $W && rsync -rlptzR --no-o --no-g -e "ssh $SSHO -p $POD_PORT" data/kalmar/tf1200_kal_sl.jsonl "root@$POD_IP:/workspace/nd-takehome/" || exit 1
