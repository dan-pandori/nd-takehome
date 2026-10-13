#!/usr/bin/env bash
# Create one A40 pod, push code + data, set up, launch the two read lanes. Usage: pod/coep/bringup.sh <pod>
export ND_RUN_ID=create-or-elicit-paper
cd /home/dan/work/create-or-elicit-paper
P=$1
echo "=== bringup $P $(date -u +%FT%TZ)"
if [ ! -f ~/.config/nd-rl/pods/$P ]; then
  ok=0
  for try in 1 2 3; do
    timeout 900 podnew $P && { ok=1; break; }
    echo "podnew $P failed (try $try); trying another data centre"
    POD_EXTRA="--data-center-ids $([ $try = 1 ] && echo EU-SE-1 || echo CA-MTL-1)" timeout 900 podnew $P && { ok=1; break; }
  done
  [ $ok = 1 ] || { echo "GIVE UP $P"; exit 1; }
fi
pod/coep/push.sh $P > /dev/null 2>&1 || { echo "push failed $P"; exit 1; }
timeout 1200 podrun $P "cd /workspace/nd-takehome && bash pod/coep/setup.sh; tail -n 3 artifacts/coe_paper/logs/setup_*.log"
timeout 60 podrun $P "cd /workspace/nd-takehome; setsid nohup bash pod/coep/lanes.sh > artifacts/coe_paper/logs/lanes.log 2>&1 < /dev/null & disown; sleep 1; echo lanes-launched"
echo "=== bringup done $(date -u +%FT%TZ)"
