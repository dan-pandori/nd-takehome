#!/usr/bin/env bash
# VPS side: start the pod-side runner for one arm.  Usage: bash pod/dsc/go.sh <arm> [N]
#   writes pod/dsc/queue.txt on the pod from jobs.py <arm> queue, then starts pod/dsc/runner.sh under setsid nohup.
# Stage-1 must already be done (bash pod/dsc/launch.sh dsc-<arm> <arm> stage1_<arm>_s0 stage1_<arm>_s1).
cd /home/dan/work/ds-composition
ARM=$1; N=${2:-3}; P=dsc-$ARM
python3 pod/dsc/jobs.py $ARM queue > /tmp/queue_$ARM.txt
bash pod/dsc/w.sh $P sh "mkdir -p pod/dsc" >/dev/null 2>&1
scp -q -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR \
    -P "$(. ~/.config/nd-rl/pods/$P; echo $POD_PORT)" /tmp/queue_$ARM.txt \
    "root@$(. ~/.config/nd-rl/pods/$P; echo $POD_IP):/workspace/nd-takehome/pod/dsc/queue.txt"
# marker file, not pgrep: the remote command line itself contains 'runner.sh' and would self-match (memory: pgrep self-match)
bash pod/dsc/w.sh $P sh "if [ -f artifacts/dsc/runner.pid ] && kill -0 \$(cat artifacts/dsc/runner.pid) 2>/dev/null; then echo 'runner already up'; exit 0; fi; N=$N setsid nohup bash pod/dsc/runner.sh > artifacts/dsc/logs/runner.log 2>&1 < /dev/null & disown; sleep 3; echo runner started; head -3 artifacts/dsc/logs/runner.log"
