#!/usr/bin/env bash
# Push the run's data (ladder pools, K12 train set) to a pod. Usage: pod/sc12/pushdata.sh <pod>
. ~/.config/nd-rl/env; N=$1; F=~/.config/nd-rl/pods/$N; [ -f "$F" ] || { echo "no pod $N"; exit 1; }; . "$F"
SSHO="-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o BatchMode=yes -o LogLevel=ERROR -o ServerAliveInterval=30"
cd /home/dan/work/state-cap12 && exec rsync -rlptzR --no-o --no-g -e "ssh $SSHO -p $POD_PORT" data/ladder/ data/kh/train_k12.jsonl "root@$POD_IP:/workspace/nd-takehome/"
