#!/usr/bin/env bash
# Wait for job done-markers, then run a queue: bash pod/r3_2/after_done.sh <jobsfile> <N> <job1> [<job2> ...]
cd /workspace/nd-takehome
Q=$1; N=$2; shift 2
for j in "$@"; do until [ -f artifacts/r3_2/logs/$j.done ]; do sleep 30; done; done
bash pod/r3_2/runq.sh $Q $N
