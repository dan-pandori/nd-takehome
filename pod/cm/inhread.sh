#!/usr/bin/env bash
# Paired control at identical read settings: inherited SN-cap12 T1 (k 32) s0-s2 on textbook72, rr600 Q, long2.
source pod/cm/env.sh
for S in ${SEEDS:-0 1 2}; do
  CK=ckpts/inh/T1_SN12_s$S.pt
  [ -s $CK ] || hf buckets cp $BK/state-cap12/ckpts/sc12/ladder/la_T1_SN12_s${S}_r8.pt $CK || exit 1
  ND_ARM=SN12 ND_SEED=$S bash pod/cm/read.sh $CK T1_SN12_s$S tb72 long2 rr600
done
md5sum ckpts/inh/*.pt
