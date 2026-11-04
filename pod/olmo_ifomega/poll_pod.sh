#!/usr/bin/env bash
# poll_pod.sh <name> <until-epoch> [conf ...]: VPS-side. Every 3 min try, in order of projected $/token for the 32B
# sampler, to create a pod; stop at the first success (writes ~/runs/olmo-ifomega/<name>.created) or at the deadline.
# conf = "<gpu id>|<count>|<COMMUNITY|SECURE>|<extra flags>"; default order below (olmo-ifomega pre-registration).
N=$1; END=$2; shift 2; L=~/runs/olmo-ifomega/poll_$N.log
export ND_RUN_ID=olmo-ifomega POD_MINCUDA=12.8
CONF=("$@")
[ ${#CONF[@]} -eq 0 ] && CONF=("NVIDIA H200|1|COMMUNITY|--public-ip" "NVIDIA A100-SXM4-80GB|2|COMMUNITY|--public-ip"
      "NVIDIA H100 80GB HBM3|2|COMMUNITY|--public-ip" "NVIDIA B200|1|COMMUNITY|--public-ip" "NVIDIA A100-SXM4-80GB|2|SECURE|"
      "NVIDIA H200|1|SECURE|" "NVIDIA B200|1|SECURE|" "NVIDIA H100 80GB HBM3|2|SECURE|")
while [ $(date +%s) -lt $END ]; do
  [ "$(rpbalance 2>/dev/null | cut -d. -f1)" -lt 60 ] && { echo "$(date -u +%T) balance low, stop" >> $L; exit 0; }
  for c in "${CONF[@]}"; do
    IFS='|' read -r POD_GPU C POD_CLOUD X <<< "$c"; export POD_GPU POD_CLOUD POD_EXTRA="--gpu-count $C --volume-in-gb 250 --container-disk-in-gb 80 $X"
    out=$(timeout 900 podnew $N 2>&1 | tail -1)
    echo "$(date -u +%T) $C x $POD_GPU $POD_CLOUD: ${out:0:120}" >> $L
    if [ -f ~/.config/nd-rl/pods/$N ]; then echo "$c" > ~/runs/olmo-ifomega/$N.created; exit 0; fi
  done
  sleep 180
done
