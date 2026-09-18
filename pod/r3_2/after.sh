#!/usr/bin/env bash
# Wait for a queue to finish, then run another: bash pod/r3_2/after.sh <queue-log-name> <jobsfile> <N>
cd /workspace/nd-takehome
until grep -q "QUEUE DONE" artifacts/$1.log 2>/dev/null; do sleep 30; done
bash pod/r3_2/runq.sh $2 $3
