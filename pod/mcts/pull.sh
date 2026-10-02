#!/usr/bin/env bash
# Pull artifacts/mcts (without the value-data feature files, which stay in the bucket) and ckpts/mcts/value_*.pt into the worktree.
. ~/.config/nd-rl/env; N=$1; F=~/.config/nd-rl/pods/$N; [ -f "$F" ] || { echo "no pod $N"; exit 1; }; . "$F" 2>/dev/null
SSHO="-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o BatchMode=yes -o LogLevel=ERROR -o ServerAliveInterval=30"
W=/home/dan/work/mcts-a
rsync -rlptz --no-o --no-g --exclude 'vdata/*.pt' -e "ssh $SSHO -p $POD_PORT" "root@$POD_IP:/workspace/nd-takehome/artifacts/mcts/" $W/artifacts/mcts/
rsync -rlptz --no-o --no-g --include 'value_*.pt' --exclude '*' -e "ssh $SSHO -p $POD_PORT" "root@$POD_IP:/workspace/nd-takehome/ckpts/mcts/" $W/ckpts/mcts/
