#!/usr/bin/env bash
# poll_pod2.sh (poll_pod.sh + POLL_SECURE=1: 1 x H200 community, then 1 x H200 secure, no back-off on a bad host; amendment 2) <name> <until-epoch> [<secure-after-epoch>]: VPS-side poller (run olmo-ifcurve). Every ~2 min try to create a
# pod with podnew2.sh (RunPod REST v2; v1 was retired 2026-11-15 and broke podnew): 1 x H200 community, then 2 x H200
# community (launch.sh checks every GPU), 200 GB volume; 1 x H200 secure only after <secure-after-epoch> if given. After
# every attempt orphans.sh lists the account (v2) and deletes any unregistered ifc-* pod. Stops at the first success
# (writes ~/runs/olmo-ifcurve/<name>.created) or at the deadline.
N=$1; END=$2; SEC=${3:-9999999999}; L=~/runs/olmo-ifcurve/poll_$N.log; W=/home/dan/work/olmo-ifcurve
export ND_RUN_ID=olmo-ifcurve POD_MINCUDA=12.8 POD_VOLUME=200 POD_DISK=60
while [ $(date +%s) -lt $END ]; do
  [ "$(rpbalance 2>/dev/null | cut -d. -f1)" -lt 45 ] && { echo "$(date -u +%T) balance low, stop" >> $L; exit 0; }
  CONF=("NVIDIA H200|1|COMMUNITY" "NVIDIA H200|2|COMMUNITY"); [ "$POLL_SECURE" = "1" ] && CONF=("NVIDIA H200|1|COMMUNITY" "NVIDIA H200|1|SECURE")
  [ $(date +%s) -ge $SEC ] && CONF+=("NVIDIA H200|1|SECURE")
  for c in "${CONF[@]}"; do
    IFS='|' read -r POD_GPU POD_COUNT POD_CLOUD <<< "$c"; export POD_GPU POD_COUNT POD_CLOUD
    out=$(timeout 1500 bash $W/pod/olmo_ifcurve/podnew2.sh $N 2>&1 | tr '\n' ' ' | tail -c 300)
    echo "$(date -u +%T) $POD_COUNT x $POD_GPU $POD_CLOUD: ${out:0:300}" >> $L
    g=$(bash $W/pod/olmo_ifcurve/orphans.sh 2>&1 | tail -1); echo "$(date -u +%T) orphan check: $g ifc pods listed" >> $L
    if [ -f ~/.config/nd-rl/pods/$N ]; then echo "$c" > ~/runs/olmo-ifcurve/$N.created; exit 0; fi
    case "$out" in *BAD_HOST*) [ "$POLL_SECURE" = "1" ] && continue; echo "$(date -u +%T) bad host again; backing off 10 min" >> $L; sleep 600; break ;; esac
  done
  sleep 100
done
