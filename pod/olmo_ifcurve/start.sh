#!/usr/bin/env bash
# start.sh: pod set-up (once), then one worker per GPU (pod/olmo_ifcurve/worker.sh), detached.
cd /workspace/nd-takehome; A=artifacts/olmo_ifcurve; mkdir -p $A/logs $A/meta
[ -f $A/meta/setup.done ] || { bash pod/olmo_ifcurve/setup.sh > $A/logs/setup.log 2>&1; grep -q SETUP_DONE $A/logs/setup.log && touch $A/meta/setup.done; }
[ -f $A/meta/setup.done ] || { echo "SETUP_FAILED $(date -u +%FT%TZ)"; exit 1; }
for g in $(seq 0 $(( $(nvidia-smi -L | wc -l) - 1 ))); do
  pgrep -f "olmo_ifcurve/worker.s[h] $g" > /dev/null || setsid nohup bash pod/olmo_ifcurve/worker.sh $g > /dev/null 2>&1 < /dev/null &
done
echo "WORKERS_STARTED $(date -u +%FT%TZ)"
