#!/usr/bin/env bash
# Start a detached job on a pod and return immediately.  Usage: pod/fsup/bg.sh <pod> <jobname> "<command>"
. ~/.config/nd-rl/env; N=$1; J=$2; shift 2; F=~/.config/nd-rl/pods/$N; [ -f "$F" ] || { echo "no pod $N"; exit 1; }; . "$F"
SSHO="-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o BatchMode=yes -o LogLevel=ERROR -o ServerAliveInterval=30"
ssh $SSHO -p "$POD_PORT" "root@$POD_IP" "cd /workspace/nd-takehome && mkdir -p artifacts/fsup/logs && rm -f artifacts/fsup/$J.done artifacts/fsup/$J.fail && setsid nohup bash -c 'source pod/fsup/env.sh; { $*; } > artifacts/fsup/logs/$J.log 2>&1 && touch artifacts/fsup/$J.done || touch artifacts/fsup/$J.fail' < /dev/null > /dev/null 2>&1 & echo started $J on $N"
