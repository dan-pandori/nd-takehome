#!/usr/bin/env bash
# Start a detached job on a pod and return immediately.  Usage: pod/sc12/bg.sh <pod> <jobname> "<command>"
. ~/.config/nd-rl/env; N=$1; J=$2; shift 2; F=~/.config/nd-rl/pods/$N; [ -f "$F" ] || { echo "no pod $N"; exit 1; }; . "$F"
SSHO="-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o BatchMode=yes -o LogLevel=ERROR -o ServerAliveInterval=30"
ssh $SSHO -p "$POD_PORT" "root@$POD_IP" "cd /workspace/nd-takehome && mkdir -p artifacts/lit-measures/m2/logs && rm -f artifacts/lit-measures/m2/$J.done artifacts/lit-measures/m2/$J.fail && setsid nohup bash -c 'source pod/lm/env.sh; { $*; } > artifacts/lit-measures/m2/logs/$J.log 2>&1 && touch artifacts/lit-measures/m2/$J.done || touch artifacts/lit-measures/m2/$J.fail' < /dev/null > /dev/null 2>&1 & echo started $J on $N"
