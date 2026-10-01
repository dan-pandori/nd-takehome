#!/usr/bin/env bash
# Pull files under 5 MB of one path from a pod (the rest is in the bucket).  Usage: pod/tj6/pullsmall.sh <pod> <relpath>
. ~/.config/nd-rl/env; N=$1; shift; F=~/.config/nd-rl/pods/$N; [ -f "$F" ] || { echo "no pod $N"; exit 1; }; . "$F" 2>/dev/null
SSHO="-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o BatchMode=yes -o LogLevel=ERROR -o ServerAliveInterval=30"
D=/home/dan/work/trajectory-cap6/$1; mkdir -p "$(dirname "$D")"
exec rsync -rlptz --no-o --no-g --max-size=5m --exclude 'dump/' -e "ssh $SSHO -p $POD_PORT" "root@$POD_IP:/workspace/nd-takehome/$1" "$(dirname "$D")/"
