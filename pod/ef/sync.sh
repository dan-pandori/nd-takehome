#!/usr/bin/env bash
# efficiency helpers (worktree ~/work/efficiency).  podsync/podpush are hardwired to ~/nd-takehome, so this run uses its own.
#   bash pod/ef/sync.sh <pod>                  push code + the data/targets/ckpts this run needs
#   bash pod/ef/sync.sh <pod> push <relpath>
#   bash pod/ef/sync.sh <pod> pull <relpath>
#   bash pod/ef/sync.sh <pod> pullall         pull artifacts/ef
. ~/.config/nd-rl/env; N=$1; shift; F=~/.config/nd-rl/pods/$N; [ -f "$F" ] || { echo "no pod $N"; exit 1; }; . "$F"
W=/home/dan/work/efficiency
SSHO="-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o BatchMode=yes -o LogLevel=ERROR -o ServerAliveInterval=30"
R="root@$POD_IP:/workspace/nd-takehome"
case "${1:-code}" in
  pull) mkdir -p "$W/$(dirname "$2")"; exec rsync -rlptz --no-o --no-g -e "ssh $SSHO -p $POD_PORT" "$R/$2" "$W/$(dirname "$2")/" ;;
  push) ssh $SSHO -p "$POD_PORT" "root@$POD_IP" "mkdir -p /workspace/nd-takehome/$(dirname "$2")"; [ -d "$W/$2" ] && set -- push "${2%/}/"; exec rsync -rlptz --no-o --no-g -e "ssh $SSHO -p $POD_PORT" "$W/$2" "$R/$2" ;;
  pullall) exec rsync -rlptz --no-o --no-g -e "ssh $SSHO -p $POD_PORT" "$R/artifacts/ef/" "$W/artifacts/ef/" ;;
  code)
    rsync -rlptz --no-o --no-g --exclude .git --exclude data/ --exclude artifacts/ --exclude ckpts/ --exclude __pycache__ --exclude .venv -e "ssh $SSHO -p $POD_PORT" "$W/" "$R/"
    ssh $SSHO -p "$POD_PORT" "root@$POD_IP" "mkdir -p /workspace/nd-takehome/{data/ladder,ckpts/ef,artifacts/ef/logs}"
    rsync -rlptz --no-o --no-g -e "ssh $SSHO -p $POD_PORT" "$W/data/heldout.jsonl" "$W/data/train.jsonl.gz" "$R/data/"
    rsync -rlptz --no-o --no-g -e "ssh $SSHO -p $POD_PORT" "$W/data/ladder/transfer.jsonl" "$R/data/ladder/"
    ;;
esac
