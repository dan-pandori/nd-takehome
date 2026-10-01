#!/usr/bin/env bash
# trajectory-cap6: score the cross targets (all three cap-6 seeds' eventual proofs + trajectory's cap-12 eventual proofs,
# data/tj6/cross.jsonl from `tj6_targets.py cross`) under all 22 checkpoints of cap-6 seed S.  Usage: bash pod/tj6/score_cross.sh <seed>
source pod/tj6/env.sh
S=$1; L=artifacts/tj6/score/ckpts_s$S.txt
[ -s $L ] || { echo "run pod/tj6/score.sh $S full first"; exit 1; }
for f in $(cut -d' ' -f2 $L); do [ -s $f ] || hf buckets cp $BK/trajectory-cap6/$f $f >/dev/null 2>&1 || { echo "MISSING $f"; exit 1; }; done
python3 tj_score.py --targets data/tj6/cross.jsonl --ckpts $L --out artifacts/tj6/score/cross_s$S --lean || exit 1
up artifacts/tj6
echo "=== score_cross $S done $(date -u +%FT%TZ)"
