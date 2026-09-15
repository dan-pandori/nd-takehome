#!/usr/bin/env bash
pkill -f 'bash /workspace/nd-takehome/pod/pod/[q]ueue2.sh'
sleep 1
cd /workspace/nd-takehome
setsid nohup bash /workspace/nd-takehome/pod/pod/[q]ueue2.sh > /workspace/nd-takehome/artifacts/queue2.log 2>&1 < /dev/null &
sleep 1
ps aux | grep -E 'bash /workspace/nd-takehome/[q]ueue2' | wc -l
