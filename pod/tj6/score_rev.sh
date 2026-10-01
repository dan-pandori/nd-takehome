#!/usr/bin/env bash
# trajectory-cap6 (added, not pre-registered): score the cross targets (data/tj6/cross.jsonl: cap-6 eventual proofs of all
# three seeds + trajectory's cap-12 eventual proofs) under all 22 checkpoints of `trajectory`'s cap-12 seed K, fetched from
# the bucket (hf://buckets/dan-pandori/nd-rl/trajectory/ckpts/tj/). The ev12s<K> rows re-score trajectory's own records
# (a consistency check).  Usage: bash pod/tj6/score_rev.sh <cap-12 seed K>
source pod/tj6/env.sh
K=$1; STEPS="0 50 100 200 400 800 1600 3000 5000 8000 12000 16000 20000"; D=ckpts/tj12
mkdir -p $D/ladder; L=artifacts/tj6/score/ckpts12_s$K.txt; : > $L
for st in $STEPS; do echo "s${K}_p$st $D/stage1_best12_s${K}_b1200_step$st.pt" >> $L; done
echo "s${K}_pend $D/stage1_best12_s${K}_b1200.pt" >> $L
for r in 1 2 3 4 5 6 7 8; do echo "s${K}_r$r $D/ladder/la_T1_best12_s${K}_r$r.pt" >> $L; done
for f in $(cut -d' ' -f2 $L); do [ -s $f ] || hf buckets cp $BK/trajectory/${f/tj12/tj} $f >/dev/null 2>&1 || { echo "MISSING $f"; exit 1; }; done
md5sum $(cut -d' ' -f2 $L) > artifacts/tj6/score/ckpts12_s$K.md5
python3 tj_score.py --targets data/tj6/cross.jsonl --ckpts $L --out artifacts/tj6/score/rev12_s$K || exit 1
up artifacts/tj6
echo "=== score_rev $K done $(date -u +%FT%TZ)"
