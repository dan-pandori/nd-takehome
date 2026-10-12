#!/usr/bin/env bash
# coe-r0: timing alone on the GPU, then the old seeds' per-round analysis (CPU) and their tracked-transfer reads.
source pod/coe/env.sh
bash pod/coe/timing.sh A40 > artifacts/coe/logs/timing_A40.log 2>&1
up artifacts/coe/timing
bash pod/coe/oldrounds.sh > artifacts/coe/logs/oldrounds.log 2>&1 &
bash pod/coe/oldreads.sh 0 > artifacts/coe/logs/oldreads_s0.log 2>&1 &
bash pod/coe/oldreads.sh 1 > artifacts/coe/logs/oldreads_s1.log 2>&1
wait
bash pod/coe/oldreads.sh 2 > artifacts/coe/logs/oldreads_s2.log 2>&1
touch artifacts/coe/markers/r0_queue.done
echo R0_QUEUE_DONE
