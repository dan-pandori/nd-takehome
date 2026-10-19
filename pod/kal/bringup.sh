#!/usr/bin/env bash
# Sequential pod bring-up (parallel podnew calls fail), then a training job.  Usage: pod/kal/bringup.sh "kal-2 D 0" ...
export ND_RUN_ID=kalmar-pretrain
cd /home/dan/work/kalmar-pretrain
for spec in "$@"; do
  set -- $spec; P=$1; ARM=$2; S=$3
  echo "=== $P $ARM s$S $(date -u +%FT%TZ)"
  if [ ! -f ~/.config/nd-rl/pods/$P ]; then
    ok=0
    for try in 1 2 3 4; do
      POD_GPU="NVIDIA GeForce RTX 3090" POD_CLOUD=COMMUNITY POD_EXTRA="--public-ip" timeout 900 podnew $P && { ok=1; break; }
      echo "podnew $P failed (try $try)"; sleep 20
    done
    [ $ok = 1 ] || { echo "GIVE UP $P"; continue; }
  fi
  pod/kal/push.sh $P > /dev/null 2>&1 || { echo "push failed $P"; continue; }
  timeout 900 podrun $P "cd /workspace/nd-takehome && bash pod/kal/setup.sh; tail -3 artifacts/kalmar/logs/setup_*.log"
  timeout 30 podrun $P "cd /workspace/nd-takehome; setsid nohup bash pod/kal/train.sh $ARM $S > /dev/null 2>&1 < /dev/null & disown; sleep 1; echo train-launched $ARM $S"
done
echo "=== bringup done $(date -u +%FT%TZ)"
