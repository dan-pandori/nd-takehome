#!/usr/bin/env bash
# Pull a reader pod's results (eval rows + summaries, read logs, registry rows) and delete the pod.  Usage: pod/tj/finish.sh <pod>
cd /home/dan/work/trajectory; P=$1; . ~/.config/nd-rl/pods/$P 2>/dev/null
S="ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o BatchMode=yes -o LogLevel=ERROR -p $POD_PORT"
rsync -rlptz --exclude '*.tmp*' -e "$S" root@$POD_IP:/workspace/nd-takehome/artifacts/tj/eval/ artifacts/tj/eval/ || exit 1
rsync -rlptz -e "$S" root@$POD_IP:/workspace/nd-takehome/artifacts/tj/logs/ artifacts/tj/logs/$P/ || exit 1
rsync -rlptz -e "$S" root@$POD_IP:/workspace/nd-takehome/artifacts/trajectory/ artifacts/trajectory/ || exit 1
$S root@$POD_IP "cd /workspace/nd-takehome && source pod/tj/env.sh && up artifacts/tj" || exit 1
podrm $P 2>&1 | tail -1
