#!/usr/bin/env bash
# Pull a reader pod's results (eval rows + summaries, read logs, registry rows) and delete the pod.  Usage: pod/tj6/finish.sh <pod>
cd /home/dan/work/trajectory-cap6; P=$1; . ~/.config/nd-rl/pods/$P 2>/dev/null
S="ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o BatchMode=yes -o LogLevel=ERROR -p $POD_PORT"
rsync -rlptz --exclude '*.tmp*' -e "$S" root@$POD_IP:/workspace/nd-takehome/artifacts/tj6/eval/ artifacts/tj6/eval/ || exit 1
rsync -rlptz -e "$S" root@$POD_IP:/workspace/nd-takehome/artifacts/tj6/logs/ artifacts/tj6/logs/$P/ || exit 1
rsync -rlptz -e "$S" root@$POD_IP:/workspace/nd-takehome/artifacts/trajectory-cap6/ artifacts/trajectory-cap6/ || exit 1
$S root@$POD_IP "cd /workspace/nd-takehome && source pod/tj6/env.sh && up artifacts/tj6" || exit 1
podrm $P 2>&1 | tail -1
