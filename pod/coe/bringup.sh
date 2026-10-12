#!/usr/bin/env bash
# Sequential pod bring-up (parallel podnew calls fail).  Usage: pod/coe/bringup.sh "coe-k1 ko 1" "coe-k2 ko 2" ...
export ND_RUN_ID=create-or-elicit
cd /home/dan/work/create-or-elicit
for spec in "$@"; do
  set -- $spec; P=$1; ARM=$2; S=$3
  echo "=== $P $ARM s$S $(date -u +%FT%TZ)"
  if [ ! -f ~/.config/nd-rl/pods/$P ]; then
    ok=0
    for try in 1 2 3; do
      timeout 900 podnew $P && { ok=1; break; }
      echo "podnew $P failed (try $try); trying EU-SE-1 / CA-MTL-1"
      POD_EXTRA="--data-center-ids $([ $try = 1 ] && echo EU-SE-1 || echo CA-MTL-1)" timeout 900 podnew $P && { ok=1; break; }
    done
    [ $ok = 1 ] || { echo "GIVE UP $P"; continue; }
  fi
  pod/coe/push.sh $P > /dev/null 2>&1 || { echo "push failed $P"; continue; }
  timeout 900 podrun $P "cd /workspace/nd-takehome && bash pod/coe/setup.sh; tail -1 artifacts/coe/logs/setup_*.log"
  pod/coe/launch.sh $P $ARM $S
  timeout 30 podrun $P "cd /workspace/nd-takehome; setsid nohup bash pod/coe/prune.sh > artifacts/coe/logs/prune.log 2>&1 < /dev/null & disown; sleep 1; echo prune-launched"
done
echo "=== bringup done $(date -u +%FT%TZ)"
