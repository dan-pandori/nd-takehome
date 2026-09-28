#!/usr/bin/env bash
# Start a detached job on a pod and return immediately.  Usage: pod/se/bg.sh <pod> <jobname> "<command>"
. ~/.config/nd-rl/env; N=$1; J=$2; shift 2; F=~/.config/nd-rl/pods/$N; [ -f "$F" ] || { echo "no pod $N"; exit 1; }; . "$F"
SSHO="-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o BatchMode=yes -o LogLevel=ERROR -o ServerAliveInterval=30"
ssh $SSHO -p "$POD_PORT" "root@$POD_IP" "cd /workspace/nd-takehome && mkdir -p artifacts/ss/logs && rm -f artifacts/ss/$J.done artifacts/ss/$J.fail && setsid nohup bash -c 'source pod/ss/env.sh; { $*; } > artifacts/ss/logs/$J.log 2>&1 && touch artifacts/ss/$J.done || touch artifacts/ss/$J.fail' < /dev/null > /dev/null 2>&1 & echo started $J on $N"
