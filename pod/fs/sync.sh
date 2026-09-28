#!/usr/bin/env bash
# fast-stage1 helpers (worktree ~/work/fast-stage1; the ~/bin podsync/podpush/podpull address ~/nd-takehome).
#   bash pod/fs/sync.sh <pod>                  push code + held-out + the control training set
#   bash pod/fs/sync.sh <pod> pull <relpath>   pull a path from the pod
#   bash pod/fs/sync.sh <pod> pullall          pull artifacts/fs/ and ckpts/fs/*.pt
#   bash pod/fs/sync.sh <pod> sh '<cmd>'       run a command in the repo on the pod
. ~/.config/nd-rl/env; N=$1; shift; F=~/.config/nd-rl/pods/$N; [ -f "$F" ] || { echo "no pod $N"; exit 1; }; . "$F"
W=/home/dan/work/fast-stage1
SSHO="-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o BatchMode=yes -o LogLevel=ERROR -o ServerAliveInterval=30"
R="root@$POD_IP:/workspace/nd-takehome"
RS() { rsync -rlptz --no-o --no-g -e "ssh $SSHO -p $POD_PORT" "$@"; }
case "${1:-code}" in
  pull) mkdir -p "$W/$(dirname "$2")"; RS "$R/$2" "$W/$(dirname "$2")/" ;;
  pullall) mkdir -p "$W/artifacts/fs" "$W/ckpts/fs"
    RS --exclude old/ "$R/artifacts/fs/" "$W/artifacts/fs/"
    RS --include '*/' --include '*.pt' --exclude '*.step*.pt' --exclude '*.state*.pt' --exclude '*' "$R/ckpts/fs/" "$W/ckpts/fs/" ;;
  sh) shift; ssh $SSHO -p "$POD_PORT" "root@$POD_IP" "cd /workspace/nd-takehome && $*" ;;
  code)
    RS --exclude .git --exclude data/ --exclude artifacts/ --exclude ckpts/ --exclude __pycache__ --exclude .venv --exclude figures/ "$W/" "$R/"
    ssh $SSHO -p "$POD_PORT" "root@$POD_IP" "mkdir -p /workspace/nd-takehome/{data/p2,ckpts/fs,artifacts/fs/logs,artifacts/fs/ev}"
    RS "$W/data/p2/heldout.jsonl" "$R/data/p2/"; RS "$W/data/heldout.jsonl" "$R/data/" ;;
  sets) RS "$W/data/p2/train_depth3_f0_a1.jsonl" "$R/data/p2/" ;;
esac
