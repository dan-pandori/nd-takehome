#!/usr/bin/env bash
# Worktree-aware pod helpers for round3-run3 (the ~/bin helpers rsync against ~/nd-takehome, which is the dan_novelty
# checkout; this run lives in the worktree /home/dan/work/round3-run3).  Usage:
#   pod/r3_3/w.sh sync <pod>              # push this worktree's code (no .git, data, artifacts, ckpts)
#   pod/r3_3/w.sh push <pod> <relpath>    # push a file or directory (trailing slash on dirs handled)
#   pod/r3_3/w.sh pull <pod> <relpath>    # pull a file or directory into this worktree
#   pod/r3_3/w.sh sh   <pod> "<cmd>"      # run a command in /workspace/nd-takehome
W=/home/dan/work/round3-run3
. ~/.config/nd-rl/env
op=$1; N=$2; shift 2; F=~/.config/nd-rl/pods/$N; [ -f "$F" ] || { echo "no pod $N"; exit 1; }; . "$F"
SSHO="-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o BatchMode=yes -o LogLevel=ERROR -o ServerAliveInterval=30"
R="root@$POD_IP"; RS="rsync -rlptz --no-o --no-g -e \"ssh $SSHO -p $POD_PORT\""
case $op in
  sync) eval $RS --delete --exclude .git --exclude data/ --exclude artifacts/ --exclude ckpts/ --exclude __pycache__ --exclude figures/ "$W/" "$R:/workspace/nd-takehome/" ;;
  push) P=$1; ssh $SSHO -p "$POD_PORT" "$R" "mkdir -p /workspace/nd-takehome/$(dirname "$P")"
        if [ -d "$W/$P" ]; then eval $RS "$W/${P%/}/" "$R:/workspace/nd-takehome/${P%/}/"; else eval $RS "$W/$P" "$R:/workspace/nd-takehome/$P"; fi ;;
  pull) P=$1; mkdir -p "$W/$(dirname "$P")"
        if ssh $SSHO -p "$POD_PORT" "$R" "test -d /workspace/nd-takehome/${P%/}"; then mkdir -p "$W/${P%/}"; eval $RS "$R:/workspace/nd-takehome/${P%/}/" "$W/${P%/}/"; else eval $RS "$R:/workspace/nd-takehome/$P" "$W/$P"; fi ;;
  sh)   ssh $SSHO -p "$POD_PORT" "$R" "mkdir -p /workspace/nd-takehome && cd /workspace/nd-takehome && $*" ;;
  *) echo "unknown op $op"; exit 1 ;;
esac
