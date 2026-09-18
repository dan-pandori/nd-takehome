#!/usr/bin/env bash
# la-4: frozen s0 (rerun after the OOM on la-1), then the T6 s0 sibling pair
cd /workspace/nd-takehome; mkdir -p artifacts/ladder
bash pod/la/arm2.sh la_frozen_s0 --seed 0 --no_train
bash pod/la/arm2.sh la_T6_s0a --seed 0 --k 16 --share_dir artifacts/ladder/share_T6_s0 --siblings 2 --sibling 0 &
bash pod/la/arm2.sh la_T6_s0b --seed 0 --k 16 --share_dir artifacts/ladder/share_T6_s0 --siblings 2 --sibling 1 &
wait; echo Q4_DONE $(date -u +%FT%TZ)
