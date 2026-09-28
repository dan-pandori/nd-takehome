#!/usr/bin/env bash
# lean-prefilter helpers (worktree ~/work/lean-prefilter; the ~/bin helpers address ~/nd-takehome, so never use podsync/podpush here).
#   bash pod/lp/sync.sh <pod>                  push code + the evaluation pools
#   bash pod/lp/sync.sh <pod> pull <relpath>   pull a path from the pod into the worktree (a directory: NO trailing slash)
#   bash pod/lp/sync.sh <pod> push <relpath>   push one path
#   bash pod/lp/sync.sh <pod> pullall          pull artifacts/lp/ and ckpts/lp/ and the assembled sets
. ~/.config/nd-rl/env; N=$1; shift; F=~/.config/nd-rl/pods/$N; [ -f "$F" ] || { echo "no pod $N"; exit 1; }; . "$F"
W=/home/dan/work/lean-prefilter
SSHO="-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o BatchMode=yes -o LogLevel=ERROR -o ServerAliveInterval=30"
R="root@$POD_IP:/workspace/nd-takehome"
RS() { rsync -rlptz --no-o --no-g -e "ssh $SSHO -p $POD_PORT" "$@"; }
case "${1:-code}" in
  pull) mkdir -p "$W/$(dirname "$2")"; RS "$R/$2" "$W/$(dirname "$2")/" ;;
  push) ssh $SSHO -p "$POD_PORT" "root@$POD_IP" "mkdir -p /workspace/nd-takehome/$(dirname "$2")"; RS "$W/$2" "$R/$2" ;;
  pullall) mkdir -p "$W/artifacts/lp"; RS --exclude 'mix_*.jsonl' "$R/artifacts/lp/" "$W/artifacts/lp/" ;;
  sh) shift; ssh $SSHO -p "$POD_PORT" "root@$POD_IP" "cd /workspace/nd-takehome && $*" ;;
  code)
    RS --exclude .git --exclude data/ --exclude artifacts/ --exclude ckpts/ --exclude __pycache__ --exclude .venv --exclude figures/ "$W/" "$R/"
    ssh $SSHO -p "$POD_PORT" "root@$POD_IP" "mkdir -p /workspace/nd-takehome/{data/ladder,data/p2,data/dsc,ckpts/lp,artifacts/lp/logs}"
    RS "$W/data/ladder/rl_targets.jsonl" "$W/data/ladder/transfer.jsonl" "$R/data/ladder/"
    RS "$W/data/p2/heldout.jsonl" "$R/data/p2/"
    ;;
esac
