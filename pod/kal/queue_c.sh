#!/usr/bin/env bash
# kal-1: wait for the KAL-C s0 pilot (launched directly), then KAL-C s1, s2.
cd /workspace/nd-takehome
while pgrep -f 'stage1_kalC_s[0].pt' > /dev/null; do sleep 20; done
touch artifacts/kalmar/logs/train_kalC_s0.done
bash pod/kal/train.sh C 1
bash pod/kal/train.sh C 2
