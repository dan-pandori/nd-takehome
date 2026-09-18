#!/usr/bin/env bash
# la-3: after T2 s0 + s1 -> T3 s0 + s1
cd /workspace/nd-takehome
until [ -f artifacts/ladder/la_T2_s0.done ] && [ -f artifacts/ladder/la_T2_s1.done ]; do sleep 60; done
bash pod/la/arm2.sh la_T3_s0 --seed 0 --relabel &
bash pod/la/arm2.sh la_T3_s1 --seed 1 --relabel &
wait; echo Q3C_DONE $(date -u +%FT%TZ)
