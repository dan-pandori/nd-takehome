#!/usr/bin/env bash
# poll_pod.sh <name> <until-epoch> [conf ...]: VPS-side (olmo-iffu's poller, run olmo-transplant). Every ~3 min try, in
# order of projected $/token for the 32B prefill-heavy sampler, to create a pod; stop at the first success (writes
# ~/runs/olmo-transplant/<name>.created) or at the deadline. conf = "<gpu id>|<count>|<COMMUNITY|SECURE>|<extra flags>".
N=$1; END=$2; shift 2; L=~/runs/olmo-transplant/poll_$N.log
export ND_RUN_ID=olmo-transplant POD_MINCUDA=12.8
CONF=("$@")
[ ${#CONF[@]} -eq 0 ] && CONF=("NVIDIA H200|2|COMMUNITY|--public-ip" "NVIDIA H200|1|COMMUNITY|--public-ip" "NVIDIA H200|1|SECURE|"
      "NVIDIA H200 NVL|1|SECURE|" "NVIDIA H200|2|SECURE|" "NVIDIA B200|1|COMMUNITY|--public-ip" "NVIDIA B200|1|SECURE|")
while [ $(date +%s) -lt $END ]; do
  [ "$(rpbalance 2>/dev/null | cut -d. -f1)" -lt 45 ] && { echo "$(date -u +%T) balance low, stop" >> $L; exit 0; }
  for c in "${CONF[@]}"; do
    IFS='|' read -r POD_GPU C POD_CLOUD X <<< "$c"; export POD_GPU POD_CLOUD POD_EXTRA="--gpu-count $C --volume-in-gb 250 --container-disk-in-gb 60 $X"
    out=$(timeout 900 podnew $N 2>&1 | tail -1)
    echo "$(date -u +%T) $C x $POD_GPU $POD_CLOUD: ${out:0:120}" >> $L
    if [ -f ~/.config/nd-rl/pods/$N ]; then echo "$c" > ~/runs/olmo-transplant/$N.created; exit 0; fi
  done
  sleep 120
done
