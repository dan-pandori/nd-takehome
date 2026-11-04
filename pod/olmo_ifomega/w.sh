#!/usr/bin/env bash
# Worktree-aware pod helpers for olmo-ifomega (the ~/bin helpers address ~/nd-takehome, not this worktree).
#   w.sh sync <pod>                       push olmo_ifomega/ (code, problem sets), olmo32/ (MathVerifier) and pod/olmo_ifomega/
#   w.sh pull <pod> <relpath>             pull a path from the pod into this worktree
#   w.sh bg <pod> <log> <script> [args]   start a pod script detached (log -> artifacts/olmo_ifomega/logs/<log>.log)
#   w.sh sh <pod> "<command>"             run a command in /workspace/nd-takehome
W=/home/dan/work/olmo-ifomega
. ~/.config/nd-rl/env; C=$1; N=$2; F=~/.config/nd-rl/pods/$N; [ -f "$F" ] || { echo "no pod $N"; exit 1; }; . "$F"
SSHO="-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o BatchMode=yes -o LogLevel=ERROR -o ServerAliveInterval=30 -o ConnectTimeout=20"
case $C in
  sync) cd $W && rsync -rlptzR --no-o --no-g --exclude __pycache__ --exclude .nltk_data -e "ssh $SSHO -p $POD_PORT" olmo_ifomega olmo32/grade.py olmo32/oi_math_utils.py pod/olmo_ifomega "root@$POD_IP:/workspace/nd-takehome/" ;;
  pull) P=${3%/}; mkdir -p "$W/$(dirname "$P")"; rsync -rlptz --no-o --no-g -e "ssh $SSHO -p $POD_PORT" "root@$POD_IP:/workspace/nd-takehome/$P" "$W/$(dirname "$P")/" ;;
  bg) L=$3; shift 3; timeout 60 ssh $SSHO -p "$POD_PORT" "root@$POD_IP" "cd /workspace/nd-takehome && mkdir -p artifacts/olmo_ifomega/logs && { setsid nohup bash $* > artifacts/olmo_ifomega/logs/$L.log 2>&1 < /dev/null & } ; sleep 1; echo started $L" ;;
  sh) shift 2; timeout 120 ssh $SSHO -p "$POD_PORT" "root@$POD_IP" "cd /workspace/nd-takehome && $*" ;;
  *) echo "usage: w.sh sync|pull|bg|sh <pod> ..."; exit 1 ;;
esac
