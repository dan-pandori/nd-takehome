#!/usr/bin/env bash
# la-2 queue (seed 1 arms). Each wave runs its arms concurrently on the one 3090 and waits.
cd /workspace/nd-takehome; mkdir -p artifacts/ladder
bash pod/la/arm.sh la_frozen_s1 --seed 1 --no_train &
bash pod/la/arm.sh la_T1_s1 --seed 1 &
wait; echo WAVE1_DONE $(date -u +%FT%TZ)
bash pod/la/arm.sh la_T4_s1 --seed 1 --alloc window &
bash pod/la/arm.sh la_T6_s1a --seed 1 --k 16 --share_dir artifacts/ladder/share_T6_s1 --siblings 2 --sibling 0 &
bash pod/la/arm.sh la_T6_s1b --seed 1 --k 16 --share_dir artifacts/ladder/share_T6_s1 --siblings 2 --sibling 1 &
wait; echo WAVE2_DONE $(date -u +%FT%TZ)
bash pod/la/arm.sh la_T5_s1 --seed 1 --inject_pool data/ladder/pool_inject_cap6.jsonl --inject_round 4 &
wait; echo WAVE3_DONE $(date -u +%FT%TZ)
echo Q2_DONE
