#!/usr/bin/env bash
# Frozen read-outs of the six new Stage-1 models, as each appears in the bucket.  Pass 1: tb72 + dev (+ held copied);
# pass 2: h250, rr600, long2.   Usage: bash pod/bs/frozen.sh
source pod/bs/env.sh
L="best6_s0 best6_s1 best6_s2 best12_s0 best12_s1 best12_s2"
get() { local CK=ckpts/bs/stage1_$1_b1200.pt
  until [ -s $CK ]; do hf buckets cp $BK/best-state/$CK $CK >/dev/null 2>&1 || sleep 60; done; }
for n in $L; do get $n; bash pod/bs/read.sh ckpts/bs/stage1_${n}_b1200.pt Fz_$n tb72 dev; done
for n in $L; do bash pod/bs/read.sh ckpts/bs/stage1_${n}_b1200.pt Fz_$n h250 long2 rr600; done
