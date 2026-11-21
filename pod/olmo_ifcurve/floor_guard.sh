#!/usr/bin/env bash
# floor_guard.sh: VPS-side balance floor for run olmo-ifcurve while the host's balance_floor / budget watchdogs cannot
# delete pods (runpodctl on REST v1). Every 5 min: if the RunPod balance is below FLOOR (default 40, the policy floor is
# 35) or this run's podbudget spend is at or above CAP (default 158 of the 160 budget), touch stop_acquire and delete
# every ifc-* pod (podrm2.sh for registered ones, rp2.py delete for the rest). Log ~/runs/olmo-ifcurve/floor_guard.log.
W=/home/dan/work/olmo-ifcurve; R=~/runs/olmo-ifcurve; L=$R/floor_guard.log; FLOOR=${FLOOR:-40}; CAP=${CAP:-158}
while true; do
  b=$(rpbalance 2>/dev/null | tail -1); s=$(podbudget 2>/dev/null | awk '$1=="olmo-ifcurve" {gsub(/\$/,"",$5); print $5}')
  if [ -n "$b" ] && awk -v b="$b" -v f="$FLOOR" 'BEGIN{exit !(b < f)}' || { [ -n "$s" ] && awk -v s="$s" -v c="$CAP" 'BEGIN{exit !(s >= c)}'; }; then
    echo "$(date -u +%FT%TZ) TRIP balance=$b spend=$s: stopping acquisition and deleting ifc pods" >> $L
    touch $R/stop_acquire
    for f in ~/.config/nd-rl/pods/ifc-*; do [ -f "$f" ] && bash $W/pod/olmo_ifcurve/podrm2.sh "$(basename $f)" >> $L 2>&1; done
    python3 $W/pod/olmo_ifcurve/rp2.py list 2>/dev/null | awk '$2 ~ /^ifc-/ {print $1}' | while read id; do python3 $W/pod/olmo_ifcurve/rp2.py delete $id >> $L 2>&1; done
    notify "olmo-ifcurve floor guard tripped" "balance=$b spend=$s; ifc pods deleted, acquisition stopped" high > /dev/null 2>&1
    exit 0
  fi
  sleep 300
done
