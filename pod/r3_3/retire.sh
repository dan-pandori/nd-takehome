#!/usr/bin/env bash
# Pull everything from a pod, diff remote vs local listings (names + sizes), print what is missing. Usage: pod/r3_3/retire.sh <pod>
cd /home/dan/work/round3-run3; P=$1; . ~/.config/nd-rl/pods/$P
SSH="ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o BatchMode=yes -o LogLevel=ERROR -p $POD_PORT"
timeout 900 pod/r3_3/w.sh pull $P artifacts/r3_3/ >/dev/null 2>&1
mkdir -p artifacts/r3_3/podlogs_$P && rsync -rlptz --no-o --no-g --include 'q_*.log' --exclude '*' -e "$SSH" root@$POD_IP:/workspace/nd-takehome/artifacts/ artifacts/r3_3/podlogs_$P/
$SSH root@$POD_IP "cd /workspace/nd-takehome/artifacts/r3_3 && find . -type f -printf '%P %s\n'; cd ../../ckpts/r3_3 && find . -type f -printf 'CK/%P %s\n'" | LC_ALL=C sort > /tmp/${P}_remote.txt
(cd artifacts/r3_3 && find . -type f -printf '%P %s\n'; cd ../../ckpts/r3_3 && find . -type f -printf 'CK/%P %s\n') | LC_ALL=C sort > /tmp/${P}_local.txt
echo "remote files: $(wc -l < /tmp/${P}_remote.txt); remote-only or size-different:"; LC_ALL=C comm -23 /tmp/${P}_remote.txt /tmp/${P}_local.txt; echo "(end)"
