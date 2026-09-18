#!/usr/bin/env bash
# round3-run4a: run the arms of several draws one after another, each as soon as its Stage-1 is done.
# usage: bash pod/r3_4a/queue.sh <ft_lr> <batch> <tag:seed> [<tag:seed> ...]
cd /workspace/nd-takehome
FTLR=$1; B=$2; shift 2
for ts in "$@"; do
  TAG=${ts%%:*}; S=${ts##*:}
  until [ -f artifacts/r3_4a/stage1_$TAG.done ]; do sleep 20; done
  bash pod/r3_4a/arms.sh $TAG $S $FTLR $B cov,ei,frozen || echo "FAILED $TAG" >> artifacts/r3_4a/queue_failed.txt
done
