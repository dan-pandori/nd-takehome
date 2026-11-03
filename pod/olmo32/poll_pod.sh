#!/usr/bin/env bash
# poll_pod.sh <name> <until-epoch>: VPS-side. Every 5 min try, in order of projected $/token, to create a pod for the
# 32B sampler; stop at the first success (writes ~/runs/olmo-think32b/<name>.created) or at the deadline.
N=$1; END=$2; L=~/runs/olmo-think32b/poll_$N.log
export ND_RUN_ID=olmo-think32b POD_MINCUDA=12.8
CONF=("NVIDIA A100-SXM4-80GB|4|COMMUNITY|--public-ip" "NVIDIA H100 NVL|4|COMMUNITY|--public-ip" "NVIDIA A100-SXM4-80GB|4|SECURE|"
      "NVIDIA H200|2|COMMUNITY|--public-ip" "NVIDIA H100 NVL|4|SECURE|" "NVIDIA H200|1|COMMUNITY|--public-ip"
      "NVIDIA H200|2|SECURE|" "NVIDIA H200|1|SECURE|")
while [ $(date +%s) -lt $END ]; do
  [ "$(rpbalance 2>/dev/null | cut -d. -f1)" -lt 60 ] && { echo "$(date -u +%T) balance low, stop" >> $L; exit 0; }
  for c in "${CONF[@]}"; do
    IFS='|' read -r POD_GPU C POD_CLOUD X <<< "$c"; export POD_GPU POD_CLOUD POD_EXTRA="--gpu-count $C --volume-in-gb 200 --container-disk-in-gb 60 $X"
    out=$(timeout 900 podnew $N 2>&1 | tail -1)
    echo "$(date -u +%T) $C x $POD_GPU $POD_CLOUD: ${out:0:100}" >> $L
    if [ -f ~/.config/nd-rl/pods/$N ]; then echo "$c" > ~/runs/olmo-think32b/$N.created; exit 0; fi
  done
  sleep 300
done
