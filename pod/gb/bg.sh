#!/usr/bin/env bash
# Start a detached job file on a pod and return at once.  Usage: pod/gb/bg.sh <pod> <jobname> <script> [args...]
. ~/.config/nd-rl/env; N=$1; J=$2; shift 2; F=~/.config/nd-rl/pods/$N; [ -f "$F" ] || { echo "no pod $N"; exit 1; }; . "$F" 2>/dev/null
SSHO="-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o BatchMode=yes -o LogLevel=ERROR -o ServerAliveInterval=30"
timeout 20 ssh $SSHO -p "$POD_PORT" "root@$POD_IP" "cd /workspace/nd-takehome && mkdir -p artifacts/gb/logs && rm -f artifacts/gb/$J.done artifacts/gb/$J.fail && setsid nohup bash -c 'bash $* > artifacts/gb/logs/$J.log 2>&1 && touch artifacts/gb/$J.done || touch artifacts/gb/$J.fail' < /dev/null > /dev/null 2>&1 & echo started $J on $N"
