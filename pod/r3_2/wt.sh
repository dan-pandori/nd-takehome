#!/usr/bin/env bash
# Worktree-aware pod transfer for round3-run2 (the ~/bin helpers use ~/nd-takehome; this run lives in ~/work/round3-run2).
#   wt.sh sync <pod>                       code of the worktree -> pod (no data/artifacts/ckpts)
#   wt.sh push <pod> <relpath> [srcroot]   file/dir -> pod (srcroot defaults to the worktree; use ~/nd-takehome for train sets / ckpts)
#   wt.sh pull <pod> <relpath>             pod -> worktree (use a trailing slash for directories)
. ~/.config/nd-rl/env; OP=$1; N=$2; F=~/.config/nd-rl/pods/$N; [ -f "$F" ] || { echo "no pod $N"; exit 1; }; . "$F"
SSHO="-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o BatchMode=yes -o LogLevel=ERROR -o ServerAliveInterval=30"
WT=/home/dan/work/round3-run2; R="root@$POD_IP:/workspace/nd-takehome"
case "$OP" in
  sync) exec rsync -rlptz --no-o --no-g --exclude .git --exclude data/ --exclude artifacts/ --exclude ckpts/ --exclude __pycache__ --exclude review_out/ -e "ssh $SSHO -p $POD_PORT" "$WT/" "$R/" ;;
  push) P=$3; SRC=${4:-$WT}; ssh $SSHO -p "$POD_PORT" "root@$POD_IP" "mkdir -p /workspace/nd-takehome/$(dirname "$P")"; exec rsync -rlptz --no-o --no-g -e "ssh $SSHO -p $POD_PORT" "$SRC/$P" "$R/$P" ;;
  pull) P=$3; mkdir -p "$WT/$(dirname "$P")"; exec rsync -rlptz --no-o --no-g -e "ssh $SSHO -p $POD_PORT" "$R/$P" "$WT/$P" ;;
  *) echo "usage: wt.sh sync|push|pull <pod> [relpath] [srcroot]"; exit 1 ;;
esac
