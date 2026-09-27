#!/usr/bin/env bash
# Pod helpers that address THIS WORKTREE instead of ~/nd-takehome (~/bin/pod* are hard-wired to
# ~/nd-takehome, which is a different checkout on this shared host).  Usage:
#   ./wt.sh sync <pod>              push code (no .git/data/artifacts/ckpts)
#   ./wt.sh push <pod> <relpath>    push one path (data/ckpts/artifacts)
#   ./wt.sh pull <pod> <relpath>    pull one path back into the worktree
WT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
. ~/.config/nd-rl/env
SSHO="-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o BatchMode=yes -o LogLevel=ERROR -o ServerAliveInterval=30"
cmd=$1; N=$2; shift 2 || true
F=~/.config/nd-rl/pods/$N; [ -f "$F" ] || { echo "no pod $N"; exit 1; }; . "$F"
case "$cmd" in
  sync) exec rsync -rlptz --no-o --no-g --delete --exclude .git --exclude data/ --exclude artifacts/ \
          --exclude ckpts/ --exclude __pycache__ --exclude figures/ --exclude nd_verify/target \
          -e "ssh $SSHO -p $POD_PORT" "$WT/" "root@$POD_IP:/workspace/nd-takehome/" ;;
  push) [ -n "$1" ] || { echo "usage: wt.sh push <pod> <relpath>"; exit 1; }
        ssh $SSHO -p "$POD_PORT" "root@$POD_IP" "mkdir -p /workspace/nd-takehome/$(dirname "$1")"
        exec rsync -rlptz --no-o --no-g -e "ssh $SSHO -p $POD_PORT" "$WT/$1" "root@$POD_IP:/workspace/nd-takehome/$1" ;;
  pull) [ -n "$1" ] || { echo "usage: wt.sh pull <pod> <relpath>"; exit 1; }
        mkdir -p "$WT/$(dirname "$1")"
        exec rsync -rlptz --no-o --no-g -e "ssh $SSHO -p $POD_PORT" "root@$POD_IP:/workspace/nd-takehome/$1" "$WT/$1" ;;
  *) echo "usage: wt.sh {sync|push|pull} <pod> [relpath]"; exit 1 ;;
esac
