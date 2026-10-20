#!/usr/bin/env bash
# Retry pod creation across GPU types until a deadline, then run the anneal job.  Usage: pod/kal/bringup_retry.sh <hours> "kal-14 0 ei" ...
export ND_RUN_ID=kalmar-pretrain
cd /home/dan/work/kalmar-pretrain
H=$1; shift; END=$(( $(date +%s) + H * 3600 ))
TRY=("NVIDIA GeForce RTX 3090|COMMUNITY|--public-ip" "NVIDIA A40|SECURE|--data-center-ids EU-SE-1" "NVIDIA A40|SECURE|--data-center-ids CA-MTL-1"
     "NVIDIA A40|SECURE|" "NVIDIA RTX A6000|SECURE|" "NVIDIA RTX A6000|COMMUNITY|--public-ip" "NVIDIA GeForce RTX 4090|COMMUNITY|--public-ip"
     "NVIDIA GeForce RTX 3090|SECURE|" "NVIDIA L40|SECURE|")
for spec in "$@"; do
  set -- $spec; P=$1; S=$2; X=$3
  while [ ! -f ~/.config/nd-rl/pods/$P ] && [ $(date +%s) -lt $END ]; do
    for t in "${TRY[@]}"; do
      IFS='|' read g c x <<< "$t"
      POD_GPU="$g" POD_CLOUD=$c POD_EXTRA="$x" timeout 900 podnew $P > /tmp/podnew_$P.log 2>&1 && { echo "$(date -u +%FT%TZ) $P on $g $c"; break; }
    done
    [ -f ~/.config/nd-rl/pods/$P ] || sleep 600
  done
  [ -f ~/.config/nd-rl/pods/$P ] || { echo "GIVE UP $P"; continue; }
  for t in 1 2 3; do pod/kal/push.sh $P > /dev/null 2>&1 && break; sleep 20; done
  timeout 900 podrun $P "cd /workspace/nd-takehome && bash pod/kal/setup.sh; tail -1 artifacts/kalmar/logs/setup_*.log"
  timeout 30 podrun $P "cd /workspace/nd-takehome; setsid nohup bash pod/kal/anneal.sh $S $X > /dev/null 2>&1 < /dev/null & disown; sleep 1; echo launched anneal $S $X"
done
echo "=== bringup_retry done $(date -u +%FT%TZ)"
