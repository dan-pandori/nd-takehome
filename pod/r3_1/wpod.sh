#!/usr/bin/env bash
# Worktree-aware copies of podsync / podpush / podpull (the ~/bin versions hard-code ~/nd-takehome).
# Usage: bash pod/r3_1/wpod.sh sync <pod> | push <pod> <relpath> | pull <pod> <relpath>
REPO=/home/dan/work/round3-run1
. ~/.config/nd-rl/env; CMD=$1; N=$2; shift 2; F=~/.config/nd-rl/pods/$N; [ -f "$F" ] || { echo "no pod $N"; exit 1; }; . "$F"
SSHO="-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o BatchMode=yes -o LogLevel=ERROR -o ServerAliveInterval=30"
case $CMD in
  sync) exec rsync -rlptz --no-o --no-g --delete --exclude .git --exclude data/ --exclude artifacts/ --exclude ckpts/ --exclude __pycache__ -e "ssh $SSHO -p $POD_PORT" $REPO/ "root@$POD_IP:/workspace/nd-takehome/";;
  push) ssh $SSHO -p "$POD_PORT" "root@$POD_IP" "mkdir -p /workspace/nd-takehome/$(dirname "$1")"; exec rsync -rLptz --no-o --no-g -e "ssh $SSHO -p $POD_PORT" "$REPO/$1" "root@$POD_IP:/workspace/nd-takehome/$1";;
  pull) mkdir -p "$REPO/$(dirname "$1")"; exec rsync -rlptz --no-o --no-g -e "ssh $SSHO -p $POD_PORT" "root@$POD_IP:/workspace/nd-takehome/$1" "$REPO/$1";;
  *) echo "usage: wpod.sh sync|push|pull <pod> [relpath]"; exit 1;;
esac
