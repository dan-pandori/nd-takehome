#!/usr/bin/env bash
# stage1-dynamics helpers (worktree ~/work/stage1-dynamics; the ~/bin helpers address ~/nd-takehome,
# so never use podsync/podpush/podpull here).
#   bash pod/sd/sync.sh <pod>                  push code + the held-out pool + the two training sets
#   bash pod/sd/sync.sh <pod> pull <relpath>   pull a path from the pod into the worktree
#   bash pod/sd/sync.sh <pod> push <relpath>   push one path
#   bash pod/sd/sync.sh <pod> pullall          pull artifacts/sd/ and the final ckpts (not the trajectory)
#   bash pod/sd/sync.sh <pod> sh '<cmd>'       run a command in the repo on the pod
. ~/.config/nd-rl/env; N=$1; shift; F=~/.config/nd-rl/pods/$N; [ -f "$F" ] || { echo "no pod $N"; exit 1; }; . "$F"
W=/home/dan/work/stage1-dynamics
SSHO="-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o BatchMode=yes -o LogLevel=ERROR -o ServerAliveInterval=30"
R="root@$POD_IP:/workspace/nd-takehome"
RS() { rsync -rlptz --no-o --no-g -e "ssh $SSHO -p $POD_PORT" "$@"; }
case "${1:-code}" in
  pull) mkdir -p "$W/$(dirname "$2")"; RS "$R/$2" "$W/$(dirname "$2")/" ;;
  push) ssh $SSHO -p "$POD_PORT" "root@$POD_IP" "mkdir -p /workspace/nd-takehome/$(dirname "$2")"; RS "$W/$2" "$R/$2" ;;
  pullall) mkdir -p "$W/artifacts/sd" "$W/ckpts/sd"
    RS "$R/artifacts/sd/" "$W/artifacts/sd/"
    RS --include '*/' --include '*.pt' --exclude '*.step*.pt' --exclude '*' "$R/ckpts/sd/" "$W/ckpts/sd/" ;;
  sh) shift; ssh $SSHO -p "$POD_PORT" "root@$POD_IP" "cd /workspace/nd-takehome && $*" ;;
  code)
    RS --exclude .git --exclude data/ --exclude artifacts/ --exclude ckpts/ --exclude __pycache__ --exclude .venv --exclude figures/ "$W/" "$R/"
    ssh $SSHO -p "$POD_PORT" "root@$POD_IP" "mkdir -p /workspace/nd-takehome/{data/p2,data/sd,ckpts/sd,artifacts/sd/logs,artifacts/sd/ev,targets}"
    RS "$W/data/p2/heldout.jsonl" "$R/data/p2/"
    ;;
  sets)   RS "$W/data/p2/train_depth3_f0_a1.jsonl" "$R/data/p2/" ;;
  fresh)  RS "$W/data/sd/train_fresh.jsonl" "$R/data/sd/" ;;
esac
