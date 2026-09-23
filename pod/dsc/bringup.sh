#!/usr/bin/env bash
# VPS side: sync code + this arm's training set to a pod and run setup.  Usage: bash pod/dsc/bringup.sh <arm>
set -e
cd /home/dan/work/ds-composition
ARM=$1; P=dsc-$ARM
bash pod/dsc/w.sh $P sync > /dev/null
if [ "$ARM" = c0 ]; then bash pod/dsc/w.sh $P push data/p2/train_depth3_f0_a1.jsonl.gz
else bash pod/dsc/w.sh $P push data/dsc/train_$ARM.jsonl.gz; fi
bash pod/dsc/w.sh $P sh "setsid nohup bash pod/dsc/setup.sh > /dev/null 2>&1 < /dev/null & disown; echo setup started on $P"
