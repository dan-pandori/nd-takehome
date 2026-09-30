#!/usr/bin/env bash
# Read-outs of the checkpoints this run did not train: state-cap12's T1 r8 (= control C s0-s3) and every Stage-1 base
# (frozen reachability).  Usage: bash pod/fsup/reread_fixed.sh
source pod/fsup/env.sh
until grep -q SETUP_DONE artifacts/fsup/setup.log 2>/dev/null; do sleep 20; done
for s in 0 1 2 3; do bash pod/fsup/reread.sh ckpts/sc12/ladder/la_T1_SN12_s${s}_r8.pt la_C_s$s; done
for s in 0 1 2 3; do bash pod/fsup/reread.sh ckpts/sc12/stage1_SN12_s$s.pt stage1_s$s; done
for s in 4 5; do CK=ckpts/fsup/stage1_SN12_s$s.pt
  until [ -s $CK ]; do hf buckets cp $BK/$CK $CK >/dev/null 2>&1 || sleep 120; done
  bash pod/fsup/reread.sh $CK stage1_s$s; done
echo "=== fixed rereads done $(date -u +%FT%TZ)"
