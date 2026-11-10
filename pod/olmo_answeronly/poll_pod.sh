#!/usr/bin/env bash
# poll_pod.sh <name> <until-epoch> <secure-after-epoch>: VPS-side (olmo-transplant's poller, run olmo-answeronly). Every
# ~2 min try to create a pod: 2 x H200 community, then 1 x H200 community; after <secure-after-epoch> also 1 x H200
# secure. Stops at the first success (writes ~/runs/olmo-answeronly/<name>.created) or at the deadline.
N=$1; END=$2; SEC=$3; L=~/runs/olmo-answeronly/poll_$N.log
export ND_RUN_ID=olmo-answeronly POD_MINCUDA=12.8
while [ $(date +%s) -lt $END ]; do
  [ "$(rpbalance 2>/dev/null | cut -d. -f1)" -lt 45 ] && { echo "$(date -u +%T) balance low, stop" >> $L; exit 0; }
  CONF=("NVIDIA H200|2|COMMUNITY|--public-ip" "NVIDIA H200|1|COMMUNITY|--public-ip")
  [ $(date +%s) -ge $SEC ] && CONF+=("NVIDIA H200|1|SECURE|")
  for c in "${CONF[@]}"; do
    IFS='|' read -r POD_GPU C POD_CLOUD X <<< "$c"; export POD_GPU POD_CLOUD POD_EXTRA="--gpu-count $C --volume-in-gb 320 --container-disk-in-gb 60 $X"
    out=$(timeout 900 podnew $N 2>&1 | tail -1)
    echo "$(date -u +%T) $C x $POD_GPU $POD_CLOUD: ${out:0:140}" >> $L
    if [ -f ~/.config/nd-rl/pods/$N ]; then echo "$c" > ~/runs/olmo-answeronly/$N.created; exit 0; fi
  done
  sleep 100
done
