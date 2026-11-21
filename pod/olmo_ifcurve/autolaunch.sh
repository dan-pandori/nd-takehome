#!/usr/bin/env bash
# autolaunch.sh <pod> [<reap args> ...]: VPS-side. Wait for the poller's ~/runs/olmo-ifcurve/<pod>.created, then run
# launch.sh <pod> (push, queue, set-up + workers) and, if reap args are given, KEEP=1 reap.sh <pod> <args> (stage-0 pulls).
N=$1; shift; W=/home/dan/work/olmo-ifcurve; L=~/runs/olmo-ifcurve/autolaunch_$N.log
until [ -f ~/runs/olmo-ifcurve/$N.created ]; do sleep 20; done
echo "$(date -u +%FT%TZ) $N created: $(cat ~/runs/olmo-ifcurve/$N.created)" >> $L
bash $W/pod/olmo_ifcurve/launch.sh $N >> $L 2>&1
echo "$(date -u +%FT%TZ) launch rc=$?" >> $L
[ $# -gt 0 ] && KEEP=1 bash $W/pod/olmo_ifcurve/reap.sh $N "$@"
echo "$(date -u +%FT%TZ) autolaunch done" >> $L
