#!/usr/bin/env bash
# Score the 8 textbook72 references found by the bound-22 minlen rerun under all 22 checkpoints of each seed.
source pod/tj/env.sh
STEPS="0 50 100 200 400 800 1600 3000 5000 8000 12000 16000 20000"
for S in 0 1 2; do
  hf buckets sync $BK/trajectory/ckpts/tj ckpts/tj --include "*best12_s${S}_*.pt" >/dev/null 2>&1 || echo "CKPT SYNC FAILED"
  L=artifacts/tj/score/ckpts_new8_s$S.txt; : > $L
  for st in $STEPS; do echo "s${S}_p$st ckpts/tj/stage1_best12_s${S}_b1200_step$st.pt" >> $L; done
  echo "s${S}_pend ckpts/tj/stage1_best12_s${S}_b1200.pt" >> $L
  for r in 1 2 3 4 5 6 7 8; do echo "s${S}_r$r ckpts/tj/ladder/la_T1_best12_s${S}_r$r.pt" >> $L; done
  python3 tj_score.py --targets data/tj/ref_new8.jsonl --ckpts $L --out artifacts/tj/score/new8_s$S --lean || exit 1
done
up artifacts/tj
