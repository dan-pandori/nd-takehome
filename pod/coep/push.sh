#!/usr/bin/env bash
# Push THIS run worktree's code (+ small data) to a pod. Usage: pod/coep/push.sh <pod>
. ~/.config/nd-rl/env; N=$1; F=~/.config/nd-rl/pods/$N; [ -f "$F" ] || { echo "no pod $N"; exit 1; }; . "$F" 2>/dev/null
W=/home/dan/work/create-or-elicit-paper
git -C $W rev-parse HEAD > $W/pod/coep/GIT_SHA
SSHO="-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o BatchMode=yes -o LogLevel=ERROR -o ServerAliveInterval=30"
rsync -rlptz --no-o --no-g --exclude .git --exclude data/ --exclude artifacts/ --exclude ckpts/ --exclude __pycache__ \
  --exclude paper/ --exclude review_coe/ -e "ssh $SSHO -p $POD_PORT" $W/ "root@$POD_IP:/workspace/nd-takehome/" || exit 1
cd $W && rsync -rlptzR --no-o --no-g -e "ssh $SSHO -p $POD_PORT" data/bs data/eval_only data/ladder data/heldout.jsonl \
  data/p2/heldout.jsonl data/coe_paper "root@$POD_IP:/workspace/nd-takehome/" || exit 1
