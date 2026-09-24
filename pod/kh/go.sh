#!/usr/bin/env bash
# VPS side: start the pod-side runner for one arm.  Usage: bash pod/kh/go.sh <arm> [N]
cd /home/dan/work/cap-horizon
ARM=$1; N=${2:-3}; P=kh-$ARM
python3 pod/kh/jobs.py $ARM queue > /tmp/queue_$ARM.txt
bash pod/kh/w.sh $P sh "mkdir -p pod/kh" >/dev/null 2>&1
scp -q -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR \
    -P "$(. ~/.config/nd-rl/pods/$P; echo $POD_PORT)" /tmp/queue_$ARM.txt \
    "root@$(. ~/.config/nd-rl/pods/$P; echo $POD_IP):/workspace/nd-takehome/pod/kh/queue.txt"
# marker file, not pgrep: the remote command line itself contains 'runner.sh' and would self-match
bash pod/kh/w.sh $P sh "if [ -f artifacts/kh/runner.pid ] && kill -0 \$(cat artifacts/kh/runner.pid) 2>/dev/null; then echo 'runner already up'; exit 0; fi; N=$N setsid nohup bash pod/kh/runner.sh > artifacts/kh/logs/runner.log 2>&1 < /dev/null & disown; sleep 3; echo runner started; head -3 artifacts/kh/logs/runner.log"
