#!/usr/bin/env bash
# Cap diagnostics: the worst action-truncation / step-cap reads again at max_action 1,024 and max_steps 192.
source pod/bs/env.sh
export MA=1024 MS=192 X=_cap
get() { [ -s $1 ] || hf buckets cp $BK/best-state/$1 $1 >/dev/null; }
for c in ckpts/bs/ladder/la_T1_best12_s1_r8.pt ckpts/bs/ladder/la_T1_best12_s2_r8.pt ckpts/bs/ladder/la_T1_best6_s0_r8.pt ckpts/bs/stage1_best6_s2_b1200.pt; do get $c; done
bash pod/bs/read.sh ckpts/bs/ladder/la_T1_best12_s1_r8.pt T1_best12_s1 tb72
bash pod/bs/read.sh ckpts/bs/ladder/la_T1_best12_s2_r8.pt T1_best12_s2 tb72
bash pod/bs/read.sh ckpts/bs/ladder/la_T1_best6_s0_r8.pt T1_best6_s0 long2
bash pod/bs/read.sh ckpts/bs/stage1_best6_s2_b1200.pt Fz_best6_s2 rr600
