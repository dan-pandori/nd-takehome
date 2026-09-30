#!/usr/bin/env bash
# After this pod's ladder writes its round-8 checkpoint, read the T1 model.  Usage: bash pod/bs/t1read.sh <cap> <seed>
source pod/bs/env.sh
CK=ckpts/bs/ladder/la_T1_best$1_s$2_r8.pt
until [ -s $CK ] && ! pgrep -f 'state_ladder_ei.p[y]' >/dev/null; do sleep 60; done
bash pod/bs/read.sh $CK T1_best$1_s$2 tb72 dev held h250 long2 rr600
