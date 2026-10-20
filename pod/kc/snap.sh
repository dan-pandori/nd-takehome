#!/usr/bin/env bash
# B1-snap on a pod: fetch kalmar-pretrain's 24 checkpoints, per-step-type code on tf1200.  Usage (via job.sh): bash pod/kc/snap.sh
. pod/kc/env.sh
C=ckpts/kc_src; L=""
for s in 0 1 2; do
  for st in _step24020 _step100000 _step200000 _step350000 _step500000 ""; do L="$L $BK/kalmar-pretrain/ckpts/kalmar/stage1_kalD_s${s}${st}.pt"; done
  L="$L $BK/kalmar-pretrain/ckpts/kalmar/stage1_kalC_s${s}.pt $BK/kalmar-pretrain/ckpts/kalmar/anneal/kalDA_s${s}.pt"
done
CK=""
for u in $L; do f=$C/$(basename $u); [ -s $f ] || hf buckets cp $u $f >/dev/null 2>&1 || echo "FETCH FAILED $u"; CK="$CK,$f"; done
PS="$C/stage1_kalD_s0.pt,$C/stage1_kalD_s1.pt,$C/stage1_kalD_s2.pt,$C/kalDA_s0.pt,$C/kalDA_s1.pt,$C/kalDA_s2.pt"
python3 kalmar_complexity/b1_snap.py --ckpts ${CK#,} --per_state $PS --out artifacts/kc/b1_snap.json
