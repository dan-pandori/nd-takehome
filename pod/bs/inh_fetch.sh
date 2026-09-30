#!/usr/bin/env bash
# Fetch the 12 inherited checkpoints (SN-cap12 T1/frozen s0-3, SN-v2 cap-6 T1/frozen s0-1) from the bucket, as textbook72 did.
source pod/bs/env.sh
for s in 0 1 2 3; do
  [ -s ckpts/inh/T1_SN12_s$s.pt ] || hf buckets cp $BK/state-cap12/ckpts/sc12/ladder/la_T1_SN12_s${s}_r8.pt ckpts/inh/T1_SN12_s$s.pt
  [ -s ckpts/inh/Fz_SN12_s$s.pt ] || hf buckets cp $BK/state-cap12/ckpts/sc12/stage1_SN12_s$s.pt ckpts/inh/Fz_SN12_s$s.pt
done
for s in 0 1; do
  [ -s ckpts/inh/T1_SN6_s$s.pt ] || hf buckets cp $BK/state-env/ckpts/se/ladder/la_T1_SN_s${s}_r8.pt ckpts/inh/T1_SN6_s$s.pt
  [ -s ckpts/inh/Fz_SN6_s$s.pt ] || hf buckets cp $BK/state-env/ckpts/se/stage1_SN_s$s.pt ckpts/inh/Fz_SN6_s$s.pt
done
md5sum ckpts/inh/*.pt
