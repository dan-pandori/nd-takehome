#!/usr/bin/env bash
# la-2: after T1 s0 -> T4 s0 + T5 s0
cd /workspace/nd-takehome
until [ -f artifacts/ladder/la_T1_s1.done ]; do sleep 60; done
bash pod/la/arm2.sh la_T4_s1 --seed 1 --alloc window &
bash pod/la/arm2.sh la_T5_s1 --seed 1 --inject_pool data/ladder/pool_inject_cap6.jsonl --inject_round 4 &
wait; echo Q2C_DONE $(date -u +%FT%TZ)
