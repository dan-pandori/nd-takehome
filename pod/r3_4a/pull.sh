#!/usr/bin/env bash
# pull artifacts/r3_4a (without the per-round training mixes) from each pod into the worktree. usage: bash pod/r3_4a/pull.sh <pod>...
W=/home/dan/work/round3-run4a
SSHO="-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o BatchMode=yes -o LogLevel=ERROR -o ServerAliveInterval=30"
for N in "$@"; do . ~/.config/nd-rl/pods/$N
  rsync -rlptz --no-o --no-g --exclude 'mix_*.jsonl' --exclude '*.out' -e "ssh $SSHO -p $POD_PORT" "root@$POD_IP:/workspace/nd-takehome/artifacts/r3_4a/" "$W/artifacts/r3_4a/" && echo "pulled $N"
  rsync -rlptz --no-o --no-g -e "ssh $SSHO -p $POD_PORT" --include 'acq_*.jsonl' --exclude '*' "root@$POD_IP:/workspace/nd-takehome/data/r3_4a/" "$W/data/r3_4a/"
done
