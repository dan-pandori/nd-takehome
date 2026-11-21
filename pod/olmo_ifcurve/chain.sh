#!/usr/bin/env bash
# chain.sh: VPS-side. After ifc-a exists, acquire ifc-b, ifc-c, ifc-d in turn (1 x / 2 x H200 community only; one
# poller at a time because parallel podnew calls fail), then launch each with its queue (olmo_ifcurve/plan/queue_<pod>.txt)
# and a reaper that pulls and verifies every job and deletes the pod. `touch ~/runs/olmo-ifcurve/stop_chain` stops it
# before the next pod.
W=/home/dan/work/olmo-ifcurve; R=~/runs/olmo-ifcurve
until [ -f $R/ifc-a.created ]; do sleep 30; done
for spec in "ifc-b|B_s0100:1200 M_s0200:2944 M_s0350:2944" "ifc-c|M_s0500:2944 M_s1100:2944" "ifc-d|B_s2300:1536 B_s0750:464"; do
  N=${spec%%|*}; J=${spec#*|}
  [ -f $R/stop_chain ] && { echo "$(date -u +%FT%TZ) stop_chain before $N" >> $R/chain.log; exit 0; }
  END=$(( $(date +%s) + 43200 ))
  echo "$(date -u +%FT%TZ) polling for $N" >> $R/chain.log
  bash $W/pod/olmo_ifcurve/poll_pod.sh $N $END $((END + 1))
  [ -f $R/$N.created ] || { echo "$(date -u +%FT%TZ) no $N by the deadline" >> $R/chain.log; continue; }
  echo "$(date -u +%FT%TZ) $N created; launching" >> $R/chain.log
  (setsid nohup bash -c "bash $W/pod/olmo_ifcurve/launch.sh $N >> $R/autolaunch_$N.log 2>&1; bash $W/pod/olmo_ifcurve/reap.sh $N $J" > /dev/null 2>&1 < /dev/null &)
done
