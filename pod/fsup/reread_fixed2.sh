#!/usr/bin/env bash
# Budget-cut version of reread_fixed.sh (10:10 UTC): C s3 on both files; every Stage-1 base on the 91 only.
source pod/fsup/env.sh
bash pod/fsup/reread.sh ckpts/sc12/ladder/la_T1_SN12_s3_r8.pt la_C_s3
for s in 0 1 2 3 4 5; do CK=ckpts/sc12/stage1_SN12_s$s.pt; [ -s $CK ] || CK=ckpts/fsup/stage1_SN12_s$s.pt
  until [ -s $CK ]; do hf buckets cp $BK/$CK $CK >/dev/null 2>&1 || sleep 60; done
  PAIRS=lp2:data/fsup/lp2_91.jsonl bash pod/fsup/reread.sh $CK stage1_s$s; done
echo "=== fixed2 done $(date -u +%FT%TZ)"
