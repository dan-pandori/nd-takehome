#!/usr/bin/env bash
# Greedy read-outs of a list of models.  Usage: bash pod/kal/queue_greedy.sh <kind> <tag>=<ckpt> ...
#   a ckpt not on disk is fetched from this run's bucket (waiting until it exists).
cd /workspace/nd-takehome; . pod/kal/env.sh
KIND=$1; shift
for tc in "$@"; do
  T=${tc%%=*}; C=${tc#*=}
  until [ -s $C ]; do hf buckets cp $BK/kalmar-pretrain/$C $C > /dev/null 2>&1 || sleep 60; done
  bash pod/kal/eval_greedy.sh $T $C $KIND 1024
done
