#!/usr/bin/env bash
# Worktree-aware pod helpers for olmo-rlzero-if (the ~/bin helpers address ~/nd-takehome, not this worktree).
#   w.sh sync <pod>                       push olmo_rlzero_if/ (code, prompt sets), the vendored IF checkers, the pilot's
#                                         weight_dist.py and pod/olmo_rlzero_if/
#   w.sh pull <pod> <relpath>             pull a path from the pod into this worktree
#   w.sh push <pod> <relpath>             push a worktree path (e.g. a partial samples file to resume) to the pod
#   w.sh bg <pod> <log> <script> [args]   start a pod script detached (log -> artifacts/olmo_rlzero_if/logs/<log>.log)
#   w.sh sh <pod> "<command>"             run a command in /workspace/nd-takehome
W=/home/dan/work/olmo-rlzero-if
. ~/.config/nd-rl/env; C=$1; N=$2; F=~/.config/nd-rl/pods/$N; [ -f "$F" ] || { echo "no pod $N"; exit 1; }; . "$F"
SSHO="-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o BatchMode=yes -o LogLevel=ERROR -o ServerAliveInterval=30 -o ConnectTimeout=20"
case $C in
  sync) cd $W && rsync -rlptzR --no-o --no-g --exclude __pycache__ -e "ssh $SSHO -p $POD_PORT" olmo_rlzero_if olmo_ifomega/vendor olmo_pilot/weight_dist.py pod/olmo_rlzero_if "root@$POD_IP:/workspace/nd-takehome/" ;;
  pull) P=${3%/}; mkdir -p "$W/$(dirname "$P")"; rsync -rlptz --no-o --no-g -e "ssh $SSHO -p $POD_PORT" "root@$POD_IP:/workspace/nd-takehome/$P" "$W/$(dirname "$P")/" ;;
  push) P=${3%/}; cd $W && rsync -rlptzR --no-o --no-g -e "ssh $SSHO -p $POD_PORT" "$P" "root@$POD_IP:/workspace/nd-takehome/" ;;
  bg) L=$3; shift 3; timeout 60 ssh $SSHO -p "$POD_PORT" "root@$POD_IP" "cd /workspace/nd-takehome && mkdir -p artifacts/olmo_rlzero_if/logs && { setsid nohup bash $* > artifacts/olmo_rlzero_if/logs/$L.log 2>&1 < /dev/null & } ; sleep 1; echo started $L" ;;
  sh) shift 2; timeout 120 ssh $SSHO -p "$POD_PORT" "root@$POD_IP" "cd /workspace/nd-takehome && $*" ;;
  *) echo "usage: w.sh sync|pull|push|bg|sh <pod> ..."; exit 1 ;;
esac
