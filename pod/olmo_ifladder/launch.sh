#!/usr/bin/env bash
# launch.sh <pod>: VPS-side; push code, inputs and the queue files, then start set-up + workers on the pod (detached).
# The queue files are artifacts/olmo_ifladder/queue/q<gpu>.txt in the worktree (append-only; pushed whole).
N=$1; W=/home/dan/work/olmo-ifladder; export POD_LOCAL_ROOT=$W
bash $W/pod/olmo_ifladder/push.sh $N
podpush $N artifacts/olmo_ifladder/queue > /dev/null 2>&1 || echo "PUSH_FAIL queue"
podrun $N "setsid nohup bash pod/olmo_ifladder/start.sh > artifacts/olmo_ifladder/logs_start.txt 2>&1 < /dev/null & disown; sleep 1; echo launched"
