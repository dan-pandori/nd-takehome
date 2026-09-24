#!/usr/bin/env bash
# VPS side: sync code + this arm's training set to a pod and run setup.  Usage: bash pod/kh/bringup.sh <arm>
set -e
cd /home/dan/work/cap-horizon
ARM=$1; P=kh-$ARM
bash pod/kh/w.sh $P sync > /dev/null
bash pod/kh/w.sh $P push data/kh/train_$ARM.jsonl.gz
bash pod/kh/w.sh $P sh "setsid nohup bash pod/kh/setup.sh > /dev/null 2>&1 < /dev/null & disown; echo setup started on $P"
