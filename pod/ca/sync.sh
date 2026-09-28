#!/usr/bin/env bash
# ckpt-avg helpers (worktree ~/work/ckpt-avg; ~/bin/podsync etc. address ~/nd-takehome, never use them here).
#   bash pod/ca/sync.sh <pod>                 push code + data/p2/heldout.jsonl + data/ca/
#   bash pod/ca/sync.sh <pod> pull <relpath>  pull a path from the pod into the worktree
#   bash pod/ca/sync.sh <pod> sh '<cmd>'      run a command in the repo on the pod
. ~/.config/nd-rl/env; N=$1; shift; F=~/.config/nd-rl/pods/$N; [ -f "$F" ] || { echo "no pod $N"; exit 1; }; . "$F" 2>/dev/null
W=/home/dan/work/ckpt-avg
SSHO="-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o BatchMode=yes -o LogLevel=ERROR -o ServerAliveInterval=30"
R="root@$POD_IP:/workspace/nd-takehome"
RS() { rsync -rlptz --no-o --no-g -e "ssh $SSHO -p $POD_PORT" "$@"; }
case "${1:-code}" in
  pull) mkdir -p "$W/$(dirname "$2")"; RS "$R/$2" "$W/$(dirname "$2")/" ;;
  sh) shift; ssh $SSHO -p "$POD_PORT" "root@$POD_IP" "cd /workspace/nd-takehome && $*" ;;
  code)
    RS --exclude .git --exclude data/ --exclude artifacts/ --exclude ckpts/ --exclude __pycache__ --exclude .venv --exclude figures/ "$W/" "$R/"
    ssh $SSHO -p "$POD_PORT" "root@$POD_IP" "mkdir -p /workspace/nd-takehome/{data/p2,data/ca,ckpts/sd,ckpts/ca,artifacts/ca/logs,artifacts/ca/ev,targets}"
    RS "$W/data/p2/heldout.jsonl" "$R/data/p2/"
    RS "$W/data/ca/" "$R/data/ca/"
    RS "$W/data/heldout.jsonl" "$R/data/"   # pod/lf/gate_selftest.py reads it
    ;;
esac
