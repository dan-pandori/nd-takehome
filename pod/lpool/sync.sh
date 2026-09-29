#!/usr/bin/env bash
# long-pool: rsync this worktree's code to a pod / pull a pod dir back.  Usage: sync.sh push <pod> | pull <pod> <relpath>
set -e; P=$2; . ~/.config/nd-rl/pods/$P
E="ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o BatchMode=yes -o LogLevel=ERROR -p $POD_PORT"
W=$(cd "$(dirname "$0")/../.." && pwd)
case $1 in
  push) rsync -az -e "$E" --exclude .git --exclude artifacts --exclude ckpts --exclude 'data/*.gz' --exclude figures ${NODATA:+--exclude /data} "$W/" root@$POD_IP:/workspace/nd-takehome/ ;;
  pull) mkdir -p "$W/$3"; rsync -az -e "$E" root@$POD_IP:/workspace/nd-takehome/$3/ "$W/$3/" ;;
esac
