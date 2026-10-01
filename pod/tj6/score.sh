#!/usr/bin/env bash
# Teacher-forced scoring of one training seed.  Usage: bash pod/tj6/score.sh <seed> [pre|full]
#   pre : reference proofs under the 14 pretraining checkpoints (intermediate figure)
#   full: eventual-proof candidates under r8 -> selection -> refs + eventual proofs under all 22 checkpoints (+ Lean check)
source pod/tj6/env.sh
S=$1; M=${2:-full}; STEPS="0 50 100 200 400 800 1600 3000 5000 8000 12000 16000 20000"
hf buckets sync $BK/trajectory-cap6/ckpts/tj6 ckpts/tj6 --include "*best6_s${S}_*.pt" >/dev/null 2>&1 || echo "CKPT SYNC FAILED"
L=artifacts/tj6/score/ckpts_s$S.txt; : > $L
for st in $STEPS; do echo "s${S}_p$st ckpts/tj6/stage1_best6_s${S}_b1200_step$st.pt" >> $L; done
echo "s${S}_pend ckpts/tj6/stage1_best6_s${S}_b1200.pt" >> $L
if [ $M = pre ]; then
  python3 tj_score.py --targets data/tj6/ref_targets.jsonl --ckpts $L --out artifacts/tj6/score/pre_s$S || exit 1
else
  for r in 1 2 3 4 5 6 7 8; do echo "s${S}_r$r ckpts/tj6/ladder/la_T1_best6_s${S}_r$r.pt" >> $L; done
  for f in $(cut -d' ' -f2 $L); do [ -s $f ] || { echo "MISSING $f"; exit 1; }; done
  md5sum $(cut -d' ' -f2 $L) > artifacts/tj6/score/ckpts_s${S}.md5
  grep " s${S}_r8 \|^s${S}_r8 " $L > artifacts/tj6/score/ckpt_r8_s$S.txt
  python3 tj6_targets.py cands --seed $S || exit 1
  python3 tj_score.py --targets data/tj6/cand_s$S.jsonl --ckpts artifacts/tj6/score/ckpt_r8_s$S.txt --out artifacts/tj6/score/cand_s$S || exit 1
  python3 tj6_targets.py select --seed $S || exit 1
  python3 tj_score.py --targets data/tj6/targets_s$S.jsonl --ckpts $L --out artifacts/tj6/score/s$S --lean || exit 1
  mkdir -p artifacts/tj6/targets; cp data/tj6/cand_s$S.jsonl data/tj6/eventual_s$S.jsonl data/tj6/targets_s$S.jsonl artifacts/tj6/targets/
fi
up artifacts/tj6
echo "=== score $S $M done $(date -u +%FT%TZ)"
