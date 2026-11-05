#!/usr/bin/env bash
# runq_after.sh <first-job-of-running-queue> <job> ...: wait until the queue started as "runq.sh <first-job> ..." has
# finished, then run runq.sh <job> ... (two queues waiting on one pod could both start a sampler in the same gap).
F=$1; shift
cd /workspace/nd-takehome
while pgrep -f "runq.sh ${F:0:1}[${F:1:1}]${F:2}" > /dev/null; do sleep 30; done
exec bash pod/olmo_ifomega/runq.sh "$@"
