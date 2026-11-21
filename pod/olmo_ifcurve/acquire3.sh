#!/usr/bin/env bash
# acquire3.sh (amendment 2: community or secure H200, the restored four-pod design): VPS-side pod orchestration (run olmo-ifcurve; replaces chain.sh / autolaunch.sh on 2026-11-21 after a pod
# with a faulty H200). For each pod name in order (PODS, default "ifc-a ifc-b ifc-c ifc-d"; ifc-a carries stage 0):
# poll for a pod (poll_pod.sh, REST v2; one creation at a time), launch it (launch.sh: push, queue, set-up + workers),
# wait for set-up's GPU verdict (meta/gpu_status, <= 30 min). A GPU_BAD pod or a set-up timeout is deleted (podrm2.sh)
# and replaced. Then its reaper starts in the background: pull and verify every job, delete the pod (ifc-a: stage-0
# pulls with KEEP=1 first). `touch ~/runs/olmo-ifcurve/stop_acquire` stops it before the next pod.
W=/home/dan/work/olmo-ifcurve; R=~/runs/olmo-ifcurve; L=$R/acquire.log; export POD_LOCAL_ROOT=$W
declare -A JOBS=([ifc-a]="M_s0050:2240 M_s1600:2944" [ifc-b]="B_s0100:1200 M_s0200:2240 M_s0350:2240"
                 [ifc-c]="M_s0500:2240 M_s1100:2944" [ifc-d]="B_s2300:1536 B_s0750:464")
log() { echo "$(date -u +%FT%TZ) $*" >> $L; }
for N in ${PODS:-ifc-a ifc-b ifc-c ifc-d}; do
  while true; do
    [ -f $R/stop_acquire ] && { log "stop_acquire before $N"; exit 0; }
    rm -f $R/$N.created
    log "polling for $N"
    POLL_SECURE=1 bash $W/pod/olmo_ifcurve/poll_pod2.sh $N $(( $(date +%s) + 43200 ))
    [ -f $R/$N.created ] || { log "no $N by the deadline"; continue 2; }
    log "$N created ($(cat $R/$N.created)); launching"
    bash $W/pod/olmo_ifcurve/launch.sh $N >> $R/autolaunch_$N.log 2>&1
    st=""
    for i in $(seq 1 90); do
      st=$(podrun $N "cat artifacts/olmo_ifcurve/meta/gpu_status 2>/dev/null" 2>/dev/null | tail -1)
      case "$st" in GPU_OK*|GPU_BAD*) break ;; esac
      sleep 20
    done
    log "$N set-up verdict: ${st:-timeout}"
    case "$st" in GPU_OK*) break ;; esac
    podrun $N "cat artifacts/olmo_ifcurve/meta/gpu_test.txt; nvidia-smi -q | grep -A3 'Remapped Rows'" >> $L 2>&1
    bash $W/pod/olmo_ifcurve/podrm2.sh $N >> $L 2>&1
    log "$N deleted (bad GPU or set-up timeout); replacing"
  done
  if [ $N = ifc-a ]; then
    (setsid nohup bash -c "KEEP=1 bash $W/pod/olmo_ifcurve/reap.sh $N M_s0050:296:M_s0050_stage0.json M_s1600:296:M_s1600_stage0.json; bash $W/pod/olmo_ifcurve/reap.sh $N ${JOBS[$N]}" > /dev/null 2>&1 < /dev/null &)
  else
    (setsid nohup bash $W/pod/olmo_ifcurve/reap.sh $N ${JOBS[$N]} > /dev/null 2>&1 < /dev/null &)
  fi
  log "$N healthy; reaper started for: ${JOBS[$N]}"
done
log "all pods acquired"
