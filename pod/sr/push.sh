#!/usr/bin/env bash
# Push THIS run worktree's code and data/{sc,sr} to a pod (podsync is hardwired to ~/nd-takehome). Usage: pod/sr/push.sh <pod>
. ~/.config/nd-rl/env; N=$1; F=~/.config/nd-rl/pods/$N; [ -f "$F" ] || { echo "no pod $N"; exit 1; }; . "$F" 2>/dev/null
SSHO="-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o BatchMode=yes -o LogLevel=ERROR -o ServerAliveInterval=30"
W=/home/dan/work/state-readouts
rsync -rlptz --no-o --no-g --exclude .git --exclude data/ --exclude artifacts/ --exclude ckpts/ --exclude __pycache__ \
  -e "ssh $SSHO -p $POD_PORT" $W/ "root@$POD_IP:/workspace/nd-takehome/" < /dev/null
ssh $SSHO -p $POD_PORT root@$POD_IP "mkdir -p /workspace/nd-takehome/data/ladder" < /dev/null
rsync -rlptz --no-o --no-g -e "ssh $SSHO -p $POD_PORT" $W/data/sc $W/data/sr "root@$POD_IP:/workspace/nd-takehome/data/" < /dev/null
