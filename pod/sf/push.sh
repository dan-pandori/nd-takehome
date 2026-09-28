#!/usr/bin/env bash
# push code + the inputs a job needs to pod $1 (trailing slashes: no nesting)
N=$1; shift; . ~/.config/nd-rl/pods/$N; WT=$(cd "$(dirname "$0")/../.." && pwd); cd $WT
SSH="ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o BatchMode=yes -o LogLevel=ERROR -p $POD_PORT"
./wt.sh sync $N >/dev/null
$SSH root@$POD_IP "cd /workspace/nd-takehome && mkdir -p data/sc data/sf data/p2 ckpts/lf ckpts/ladder ckpts/sf artifacts/sf/logs"
for p in "$@"; do if [ -d "$p" ]; then rsync -az -e "$SSH" "$p/" "root@$POD_IP:/workspace/nd-takehome/$p/"; else rsync -az -e "$SSH" "$p" "root@$POD_IP:/workspace/nd-takehome/$(dirname $p)/"; fi || echo "FAIL $p"; done
