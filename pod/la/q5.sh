#!/usr/bin/env bash
# la-5: the T6 s1 sibling pair
cd /workspace/nd-takehome; mkdir -p artifacts/ladder
bash pod/la/arm2.sh la_T6_s1a --seed 1 --k 16 --share_dir artifacts/ladder/share_T6_s1 --siblings 2 --sibling 0 &
bash pod/la/arm2.sh la_T6_s1b --seed 1 --k 16 --share_dir artifacts/ladder/share_T6_s1 --siblings 2 --sibling 1 &
wait; echo Q5_DONE $(date -u +%FT%TZ)
