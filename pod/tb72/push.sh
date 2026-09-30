#!/usr/bin/env bash
# Push THIS worktree's code + the 72 problems + the pools the scripts read to a pod (podsync is hardwired to ~/nd-takehome).
# Usage: pod/tb72/push.sh <pod>
. ~/.config/nd-rl/env; N=$1; F=~/.config/nd-rl/pods/$N; [ -f "$F" ] || { echo "no pod $N"; exit 1; }; . "$F"
SSHO="-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o BatchMode=yes -o LogLevel=ERROR -o ServerAliveInterval=30"
cd /home/dan/work/textbook72 || exit 1
rsync -rlptz --no-o --no-g --exclude .git --exclude data/ --exclude artifacts/ --exclude ckpts/ --exclude __pycache__ \
  -e "ssh $SSHO -p $POD_PORT" ./ "root@$POD_IP:/workspace/nd-takehome/" &&
rsync -rlptzR --no-o --no-g -e "ssh $SSHO -p $POD_PORT" data/eval_only/textbook72/ data/ladder/rl_targets.jsonl data/rl_targets.jsonl \
  "root@$POD_IP:/workspace/nd-takehome/"
