#!/usr/bin/env bash
# Bring up the A40s for the KAL-D phase, one at a time (parallel podnew calls fail).  Each job waits for its checkpoint
# in the bucket.  Usage: pod/kal/bringup_D.sh "kal-9 read 0" "kal-10 read 1" "kal-11 read 2" "kal-12 ei 0" "kal-13 frozen 0"
export ND_RUN_ID=kalmar-pretrain
cd /home/dan/work/kalmar-pretrain
for spec in "$@"; do
  set -- $spec; P=$1; JOB=$2; S=$3
  echo "=== $P $JOB s$S $(date -u +%FT%TZ)"
  if [ ! -f ~/.config/nd-rl/pods/$P ]; then
    ok=0
    for try in 1 2 3; do
      POD_GPU="NVIDIA A40" timeout 900 podnew $P && { ok=1; break; }
      POD_GPU="NVIDIA A40" POD_EXTRA="--data-center-ids $([ $try = 1 ] && echo EU-SE-1 || echo CA-MTL-1)" timeout 900 podnew $P && { ok=1; break; }
      sleep 30
    done
    [ $ok = 1 ] || { echo "GIVE UP $P"; continue; }
  fi
  pod/kal/push.sh $P > /dev/null 2>&1 || { echo "push failed $P"; continue; }
  timeout 900 podrun $P "cd /workspace/nd-takehome && bash pod/kal/setup.sh; tail -1 artifacts/kalmar/logs/setup_*.log; df -h /workspace | tail -1"
  if [ $JOB = read ]; then
    timeout 30 podrun $P "cd /workspace/nd-takehome; setsid nohup bash pod/kal/queue_sampled.sh kal:kalD_s$S=ckpts/kalmar/stage1_kalD_s$S.pt > artifacts/kalmar/logs/queue_sampled_D$S.log 2>&1 < /dev/null & disown; sleep 1; echo launched read $S"
  else
    timeout 30 podrun $P "cd /workspace/nd-takehome; setsid nohup bash pod/kal/ladder.sh $JOB $S > /dev/null 2>&1 < /dev/null & disown; sleep 1; echo launched ladder $JOB $S"
  fi
done
echo "=== bringup_D done $(date -u +%FT%TZ)"
