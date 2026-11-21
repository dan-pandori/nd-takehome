#!/usr/bin/env bash
# launch.sh <pod>: VPS-side; push code and inputs, install olmo_ifcurve/plan/queue_<pod>.txt as the pod's queue
# artifacts/olmo_ifcurve/queue/q0.txt (a 2-GPU pod with queue_<pod>_2gpu_g0/g1.txt gets those as q0 / q1), then start set-up + workers on the pod (detached). Later lines are appended on the
# pod (`podrun <pod> "echo '<line>' >> artifacts/olmo_ifcurve/queue/q0.txt"`); the worker re-reads the file per line.
N=$1; W=/home/dan/work/olmo-ifcurve; export POD_LOCAL_ROOT=$W
[ -f $W/olmo_ifcurve/plan/queue_$N.txt ] || { echo "no queue file olmo_ifcurve/plan/queue_$N.txt"; exit 1; }
bash $W/pod/olmo_ifcurve/push.sh $N
NG=$(podrun $N "nvidia-smi -L | wc -l" 2>/dev/null | tail -1); echo "GPUs: $NG"
mkdir -p $W/artifacts/olmo_ifcurve/queue && rm -f $W/artifacts/olmo_ifcurve/queue/q*.txt
if [ "$NG" = "2" ] && [ -f $W/olmo_ifcurve/plan/queue_${N}_2gpu_g0.txt ]; then
  cp $W/olmo_ifcurve/plan/queue_${N}_2gpu_g0.txt $W/artifacts/olmo_ifcurve/queue/q0.txt
  cp $W/olmo_ifcurve/plan/queue_${N}_2gpu_g1.txt $W/artifacts/olmo_ifcurve/queue/q1.txt
else cp $W/olmo_ifcurve/plan/queue_$N.txt $W/artifacts/olmo_ifcurve/queue/q0.txt; touch $W/artifacts/olmo_ifcurve/queue/q1.txt; fi
podpush $N artifacts/olmo_ifcurve/queue > /dev/null 2>&1 || echo "PUSH_FAIL queue"
podrun $N "setsid nohup bash pod/olmo_ifcurve/start.sh > artifacts/olmo_ifcurve/logs_start.txt 2>&1 < /dev/null & disown; sleep 1; echo launched"
