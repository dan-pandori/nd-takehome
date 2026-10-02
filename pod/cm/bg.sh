#!/usr/bin/env bash
# Start a detached job on a pod and return immediately.  Usage: pod/cm/bg.sh <pod> <jobname> "<command>"
. ~/.config/nd-rl/env; N=$1; J=$2; shift 2; F=~/.config/nd-rl/pods/$N; [ -f "$F" ] || { echo "no pod $N"; exit 1; }; . "$F" 2>/dev/null
SSHO="-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o BatchMode=yes -o LogLevel=ERROR -o ServerAliveInterval=30"
timeout 20 ssh $SSHO -p "$POD_PORT" "root@$POD_IP" "cd /workspace/nd-takehome && mkdir -p artifacts/cm/logs && rm -f artifacts/cm/$J.done artifacts/cm/$J.fail && setsid nohup bash -c 'source pod/cm/env.sh; { $*; } > artifacts/cm/logs/$J.log 2>&1 && touch artifacts/cm/$J.done || touch artifacts/cm/$J.fail' < /dev/null > /dev/null 2>&1 & echo started $J on $N"
