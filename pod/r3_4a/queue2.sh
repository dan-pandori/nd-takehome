#!/usr/bin/env bash
# round3-run4a: like queue.sh, but OOM-tolerant: a failed arms.sh (resumable) is retried after a pause, up to 30 times.
# usage: bash pod/r3_4a/queue2.sh <ft_lr> <batch> <stages> <tag:seed> [<tag:seed> ...]
cd /workspace/nd-takehome
FTLR=$1; B=$2; ST=$3; shift 3
for ts in "$@"; do
  TAG=${ts%%:*}; S=${ts##*:}
  until [ -f artifacts/r3_4a/stage1_$TAG.done ]; do sleep 20; done
  n=0
  until bash pod/r3_4a/arms.sh $TAG $S $FTLR $B $ST; do
    n=$((n+1)); echo "$(date -u +%T) retry $n $TAG" >> artifacts/r3_4a/queue_retries.txt
    [ $n -ge 30 ] && { echo "FAILED $TAG" >> artifacts/r3_4a/queue_failed.txt; break; }
    sleep 90
  done
done
