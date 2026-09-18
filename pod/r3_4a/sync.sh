#!/usr/bin/env bash
# round3-run4a helpers (worktree ~/work/round3-run4a, not ~/nd-takehome). Usage:
#   bash pod/r3_4a/sync.sh <pod>                  push code (no .git/data/artifacts/ckpts) + targets/ + the run's small data files
#   bash pod/r3_4a/sync.sh <pod> pull <relpath>   pull a path from the pod into the worktree (into its parent dir)
#   bash pod/r3_4a/sync.sh <pod> push <relpath>   push a path from the worktree to the pod
. ~/.config/nd-rl/env; N=$1; shift; F=~/.config/nd-rl/pods/$N; [ -f "$F" ] || { echo "no pod $N"; exit 1; }; . "$F"
W=/home/dan/work/round3-run4a
SSHO="-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o BatchMode=yes -o LogLevel=ERROR -o ServerAliveInterval=30"
R="root@$POD_IP:/workspace/nd-takehome"
case "${1:-code}" in
  pull) mkdir -p "$W/$(dirname "$2")"; exec rsync -rlptz --no-o --no-g -e "ssh $SSHO -p $POD_PORT" "$R/$2" "$W/$(dirname "$2")/" ;;
  push) ssh $SSHO -p "$POD_PORT" "root@$POD_IP" "mkdir -p /workspace/nd-takehome/$(dirname "$2")"; exec rsync -rlptz --no-o --no-g -e "ssh $SSHO -p $POD_PORT" "$W/$2" "$R/$2" ;;
  code)
    rsync -rlptz --no-o --no-g --exclude .git --exclude data/ --exclude artifacts/ --exclude ckpts/ --exclude figures/ --exclude __pycache__ --exclude .venv -e "ssh $SSHO -p $POD_PORT" "$W/" "$R/"
    ssh $SSHO -p "$POD_PORT" "root@$POD_IP" "mkdir -p /workspace/nd-takehome/data/p2 /workspace/nd-takehome/data/r3_4a /workspace/nd-takehome/ckpts/r3_4a /workspace/nd-takehome/artifacts/r3_4a /workspace/nd-takehome/targets"
    rsync -rlptz --no-o --no-g -e "ssh $SSHO -p $POD_PORT" "$W/targets/" "$R/targets/"
    rsync -rlptz --no-o --no-g -e "ssh $SSHO -p $POD_PORT" "$W/data/p2/heldout.jsonl" "$W"/data/p2/targets_reductio*.jsonl "$W"/data/p2/transfer_reductio*.jsonl "$R/data/p2/"
    ;;
esac
