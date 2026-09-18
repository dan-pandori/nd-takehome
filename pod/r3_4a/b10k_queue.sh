#!/usr/bin/env bash
# round3-run4a: after <wait marker> exists, run b10k.sh for each tag in turn (retrying on OOM). usage: b10k_queue.sh <marker> <batch> <tag>...
cd /workspace/nd-takehome
M=$1; B=$2; shift 2
until [ -f artifacts/r3_4a/$M ]; do sleep 30; done
for TAG in "$@"; do
  until [ -f artifacts/r3_4a/ei_$TAG.done ]; do sleep 30; done
  n=0; until bash pod/r3_4a/b10k.sh $TAG $B; do n=$((n+1)); echo "$(date -u +%T) b10k retry $n $TAG" >> artifacts/r3_4a/queue_retries.txt; [ $n -ge 30 ] && break; sleep 90; done
done
