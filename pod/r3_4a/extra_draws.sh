#!/usr/bin/env bash
# round3-run4a EXPLORATORY: extra 85M config-A Stage-1 draws, pre-RL coverage only (non-zero fraction at 85M). usage: extra_draws.sh <seed> <seed>
cd /workspace/nd-takehome
until [ -f artifacts/r3_4a/$WAIT ]; do sleep 20; done
for s in "$@"; do ( bash pod/r3_4a/stage1.sh m85 $s A && n=0; until COVB=1000 bash pod/r3_4a/arms.sh m85_s$s $s 1e-4 1024 cov; do n=$((n+1)); [ $n -ge 30 ] && break; sleep 90; done ) > artifacts/r3_4a/extra_m85_s$s.out 2>&1 & sleep 60; done
wait
