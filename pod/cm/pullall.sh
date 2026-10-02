#!/usr/bin/env bash
# Pull this run's small files from a pod (eval, ladder dirs without mix_*.jsonl, logs, registry rows).  Usage: pod/cm/pullall.sh <pod>
. ~/.config/nd-rl/env; . ~/.config/nd-rl/pods/$1
exec rsync -rlptz --no-o --no-g --exclude 'dump/' --exclude 'mix_*.jsonl' \
  -e "ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o BatchMode=yes -o LogLevel=ERROR -p $POD_PORT" \
  "root@$POD_IP:/workspace/nd-takehome/artifacts/cm" "root@$POD_IP:/workspace/nd-takehome/artifacts/compute-match" artifacts/
