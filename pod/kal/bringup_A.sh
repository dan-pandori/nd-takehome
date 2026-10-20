#!/usr/bin/env bash
# Pods for Addendum 3's anneal control, one at a time.  Usage: pod/kal/bringup_A.sh "kal-14 0 ei" "kal-15 1" "kal-16 2"
export ND_RUN_ID=kalmar-pretrain
cd /home/dan/work/kalmar-pretrain
for spec in "$@"; do
  set -- $spec; P=$1; S=$2; X=$3
  echo "=== $P s$S $X $(date -u +%FT%TZ)"
  if [ ! -f ~/.config/nd-rl/pods/$P ]; then
    POD_GPU="NVIDIA GeForce RTX 3090" POD_CLOUD=COMMUNITY POD_EXTRA="--public-ip" timeout 900 podnew $P \
      || POD_GPU="NVIDIA A40" timeout 900 podnew $P || { echo "GIVE UP $P"; continue; }
  fi
  for t in 1 2 3; do pod/kal/push.sh $P > /dev/null 2>&1 && break; echo "push retry $t"; sleep 20; done
  timeout 900 podrun $P "cd /workspace/nd-takehome && bash pod/kal/setup.sh; tail -1 artifacts/kalmar/logs/setup_*.log"
  timeout 30 podrun $P "cd /workspace/nd-takehome; setsid nohup bash pod/kal/anneal.sh $S $X > /dev/null 2>&1 < /dev/null & disown; sleep 1; echo launched anneal $S $X"
done
echo "=== bringup_A done $(date -u +%FT%TZ)"
