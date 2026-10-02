#!/usr/bin/env bash
# Pull artifacts/oa (+ registry rows) from a pod.  Usage: pod/oa/pull.sh <pod>
. ~/.config/nd-rl/env; N=$1; F=~/.config/nd-rl/pods/$N; [ -f "$F" ] || { echo "no pod $N"; exit 1; }; . "$F" 2>/dev/null
SSHO="-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o BatchMode=yes -o LogLevel=ERROR -o ServerAliveInterval=30"
W=/home/dan/work/organism-analysis
rsync -rlptz --no-o --no-g -e "ssh $SSHO -p $POD_PORT" "root@$POD_IP:/workspace/nd-takehome/artifacts/oa" $W/artifacts/
rsync -rlptz --no-o --no-g -e "ssh $SSHO -p $POD_PORT" "root@$POD_IP:/workspace/nd-takehome/artifacts/organism-analysis" $W/artifacts/ 2>/dev/null
true
