#!/usr/bin/env bash
# Start a detached job on a pod and return immediately.  Usage: pod/tj6/bg.sh <pod> <jobname> "<command>"
. ~/.config/nd-rl/env; N=$1; J=$2; shift 2; F=~/.config/nd-rl/pods/$N; [ -f "$F" ] || { echo "no pod $N"; exit 1; }; . "$F" 2>/dev/null
SSHO="-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o BatchMode=yes -o LogLevel=ERROR -o ServerAliveInterval=30"
timeout 20 ssh $SSHO -p "$POD_PORT" "root@$POD_IP" "cd /workspace/nd-takehome && mkdir -p artifacts/tj6/logs && rm -f artifacts/tj6/$J.done artifacts/tj6/$J.fail && setsid nohup bash -c 'source pod/tj6/env.sh; { $*; } > artifacts/tj6/logs/$J.log 2>&1 && touch artifacts/tj6/$J.done || touch artifacts/tj6/$J.fail' < /dev/null > /dev/null 2>&1 & echo started $J on $N"
