#!/usr/bin/env bash
# Push origin/dan's tree (the trainer before --data_seed) to /workspace/orig on a pod. Usage: pod/lm/push_orig.sh <pod>
. ~/.config/nd-rl/env; N=$1; F=~/.config/nd-rl/pods/$N; [ -f "$F" ] || { echo "no pod $N"; exit 1; }; . "$F"
SSHO="-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o BatchMode=yes -o LogLevel=ERROR -o ServerAliveInterval=30"
T=$(mktemp -d); cd /home/dan/work/lit-measures && git archive origin/dan -- '*.py' tests/fixtures | tar -x -C $T
ssh $SSHO -p $POD_PORT root@$POD_IP "mkdir -p /workspace/orig/data" && \
rsync -rlptz --no-o --no-g -e "ssh $SSHO -p $POD_PORT" $T/ root@$POD_IP:/workspace/orig/ && rm -rf $T
ssh $SSHO -p $POD_PORT root@$POD_IP "ln -sfn /workspace/nd-takehome/data/nf /workspace/orig/data/nf; ln -sfn /workspace/nd-takehome/data/p2 /workspace/orig/data/p2; echo orig ok"
