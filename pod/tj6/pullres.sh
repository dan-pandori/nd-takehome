#!/usr/bin/env bash
# Pull a pod's finished results (eval rows + summaries, score dirs, logs under logs/<pod>/, registry rows) without deleting it.
# Usage: pod/tj6/pullres.sh <pod>
cd /home/dan/work/trajectory-cap6; P=$1; . ~/.config/nd-rl/pods/$P 2>/dev/null
S="ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o BatchMode=yes -o LogLevel=ERROR -p $POD_PORT"
mkdir -p artifacts/tj6/eval artifacts/tj6/score artifacts/tj6/logs/$P
rsync -rlptz --exclude '*.tmp*' -e "$S" root@$POD_IP:/workspace/nd-takehome/artifacts/tj6/eval/ artifacts/tj6/eval/ || exit 1
rsync -rlptz -e "$S" root@$POD_IP:/workspace/nd-takehome/artifacts/tj6/score/ artifacts/tj6/score/ || exit 1
rsync -rlptz -e "$S" root@$POD_IP:/workspace/nd-takehome/artifacts/tj6/logs/ artifacts/tj6/logs/$P/ || exit 1
$S root@$POD_IP "test -d /workspace/nd-takehome/artifacts/trajectory-cap6" && { rsync -rlptz -e "$S" root@$POD_IP:/workspace/nd-takehome/artifacts/trajectory-cap6/ artifacts/trajectory-cap6/ || exit 1; }
exit 0
