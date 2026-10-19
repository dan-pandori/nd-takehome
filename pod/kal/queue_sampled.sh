#!/usr/bin/env bash
# Sampled read-outs (batch 2,048) of a list of models.  Usage: bash pod/kal/queue_sampled.sh <kind>:<tag>=<ckpt> ...
#   kind kal (KAL-D, with the k extension), kalC (KAL-C, k 32 only), ctl (control, + k 256 where no stored read)
#   a ckpt not on disk is fetched from this run's bucket (best-state's for ckpts/ctl/), waiting until it exists.
cd /workspace/nd-takehome; . pod/kal/env.sh
for spec in "$@"; do
  KIND=${spec%%:*}; tc=${spec#*:}; T=${tc%%=*}; C=${tc#*=}
  if [ "$KIND" = ctl ]; then SRC=$BK/best-state/ckpts/bs/$(basename $C); else SRC=$BK/kalmar-pretrain/$C; fi
  mkdir -p $(dirname $C)
  until [ -s $C ]; do hf buckets cp $SRC $C > /dev/null 2>&1 || sleep 60; done
  if [ "$KIND" = kalC ]; then EXT=0 bash pod/kal/eval_sampled.sh $T $C kal 2048; else bash pod/kal/eval_sampled.sh $T $C $KIND 2048; fi
done
