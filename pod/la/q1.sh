#!/usr/bin/env bash
# la-1 queue (seed 0 arms). Each wave runs its arms concurrently on the one 3090 and waits.
cd /workspace/nd-takehome; mkdir -p artifacts/ladder
bash pod/la/arm.sh la_frozen_s0 --seed 0 --no_train &
bash pod/la/arm.sh la_T1_s0 --seed 0 &
wait; echo WAVE1_DONE $(date -u +%FT%TZ)
bash pod/la/arm.sh la_T4_s0 --seed 0 --alloc window &
bash pod/la/arm.sh la_T6_s0a --seed 0 --k 16 --share_dir artifacts/ladder/share_T6_s0 --siblings 2 --sibling 0 &
bash pod/la/arm.sh la_T6_s0b --seed 0 --k 16 --share_dir artifacts/ladder/share_T6_s0 --siblings 2 --sibling 1 &
wait; echo WAVE2_DONE $(date -u +%FT%TZ)
bash pod/la/arm.sh la_T5_s0 --seed 0 --inject_pool data/ladder/pool_inject_cap6.jsonl --inject_round 4 &
wait; echo WAVE3_DONE $(date -u +%FT%TZ)
echo Q1_DONE
