#!/usr/bin/env bash
# Worktree-aware pod helpers for olmo-rlzero-pilot (the ~/bin helpers address ~/nd-takehome, not this worktree).
#   w.sh sync <pod>              push olmo_pilot/ and pod/olmo_pilot/ (code + manifest) to the pod
#   w.sh pull <pod> <relpath>    pull a path from the pod into this worktree
#   w.sh bg <pod> <log> <script> [args]   start a pod script detached (log -> artifacts/olmo_pilot/logs/<log>.log)
W=/home/dan/work/olmo-rlzero-pilot
. ~/.config/nd-rl/env; C=$1; N=$2; F=~/.config/nd-rl/pods/$N; [ -f "$F" ] || { echo "no pod $N"; exit 1; }; . "$F"
SSHO="-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o BatchMode=yes -o LogLevel=ERROR -o ServerAliveInterval=30 -o ConnectTimeout=20"
case $C in
  sync) cd $W && rsync -rlptzR --no-o --no-g --exclude __pycache__ -e "ssh $SSHO -p $POD_PORT" olmo_pilot pod/olmo_pilot "root@$POD_IP:/workspace/nd-takehome/" ;;
  pull) P=${3%/}; mkdir -p "$W/$(dirname "$P")"; rsync -rlptz --no-o --no-g -e "ssh $SSHO -p $POD_PORT" "root@$POD_IP:/workspace/nd-takehome/$P" "$W/$(dirname "$P")/" ;;
  bg) L=$3; shift 3; timeout 60 ssh $SSHO -p "$POD_PORT" "root@$POD_IP" "cd /workspace/nd-takehome && mkdir -p artifacts/olmo_pilot/logs && { setsid nohup bash $* > artifacts/olmo_pilot/logs/$L.log 2>&1 < /dev/null & } ; sleep 1; echo started $L" ;;
  *) echo "usage: w.sh sync|pull|bg <pod> ..."; exit 1 ;;
esac
