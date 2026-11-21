#!/usr/bin/env bash
# poll_pod.sh <name> <until-epoch> [<secure-after-epoch>]: VPS-side (olmo-transplant's poller, run olmo-ifcurve). Every
# ~2 min try to create a pod: 1 x H200 community, then 2 x H200 community (launch.sh checks every GPU), 200 GB volume;
# 1 x H200 secure only after <secure-after-epoch> if given. Since 2026-11-21 08:33 (17 pods leaked while rest.runpod.io
# was NXDOMAIN): no create while rest.runpod.io does not resolve, and orphans.sh (GraphQL listing; deletes unregistered
# ifc-* pods) after every attempt. Stops at the first success (writes ~/runs/olmo-ifcurve/<name>.created) or the deadline.
N=$1; END=$2; SEC=${3:-9999999999}; L=~/runs/olmo-ifcurve/poll_$N.log; W=/home/dan/work/olmo-ifcurve
export ND_RUN_ID=olmo-ifcurve POD_MINCUDA=12.8
while [ $(date +%s) -lt $END ]; do
  [ "$(rpbalance 2>/dev/null | cut -d. -f1)" -lt 45 ] && { echo "$(date -u +%T) balance low, stop" >> $L; exit 0; }
  if ! getent hosts rest.runpod.io > /dev/null; then echo "$(date -u +%T) rest.runpod.io does not resolve; no create" >> $L; sleep 300; continue; fi
  CONF=("NVIDIA H200|1|COMMUNITY|--public-ip" "NVIDIA H200|2|COMMUNITY|--public-ip")
  [ $(date +%s) -ge $SEC ] && CONF+=("NVIDIA H200|1|SECURE|")
  for c in "${CONF[@]}"; do
    getent hosts rest.runpod.io > /dev/null || break
    IFS='|' read -r POD_GPU C POD_CLOUD X <<< "$c"; export POD_GPU POD_CLOUD POD_EXTRA="--gpu-count $C --volume-in-gb 200 --container-disk-in-gb 60 $X"
    out=$(timeout 900 podnew $N 2>&1 | tr '\n' ' ' | tail -c 300)
    echo "$(date -u +%T) $C x $POD_GPU $POD_CLOUD: ${out:0:300}" >> $L
    g=$(bash $W/pod/olmo_ifcurve/orphans.sh 2>&1 | tail -1); echo "$(date -u +%T) orphan check: $g ifc pods listed" >> $L
    if [ -f ~/.config/nd-rl/pods/$N ]; then echo "$c" > ~/runs/olmo-ifcurve/$N.created; exit 0; fi
  done
  sleep 100
done
