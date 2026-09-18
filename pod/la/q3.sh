#!/usr/bin/env bash
# la-3 queue: T2 (both seeds), then T3 (both seeds).
cd /workspace/nd-takehome; mkdir -p artifacts/ladder
bash pod/la/arm.sh la_T2_s0 --seed 0 --alloc difficulty &
bash pod/la/arm.sh la_T2_s1 --seed 1 --alloc difficulty &
wait; echo WAVE1_DONE $(date -u +%FT%TZ)
bash pod/la/arm.sh la_T3_s0 --seed 0 --relabel &
bash pod/la/arm.sh la_T3_s1 --seed 1 --relabel &
wait; echo WAVE2_DONE $(date -u +%FT%TZ)
echo Q3_DONE
