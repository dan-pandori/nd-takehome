#!/usr/bin/env bash
# Reviewer (coe-dose01): download the run's small raw files from the bucket, one at a time.
BK=hf://buckets/dan-pandori/nd-rl/coe-dose01
D=~/review/cd01_big
get() { [ -s "$2" ] && return; hf buckets cp "$BK/$1" "$2" >/dev/null 2>&1 || echo "FAILED $1"; }
for S in 0 1 2; do
  for R in $(seq 1 16); do get artifacts/coe/ladder/la_dose01_s$S/alloc_$R.json $D/alloc/dose01_s${S}_$R.json; done
  get artifacts/coe/eval/pend_dose01_s${S}_x0.jsonl.gz $D/reads/pend_dose01_s${S}_x0.jsonl.gz
  get artifacts/coe/eval/r16_dose01_s${S}_x0.jsonl.gz $D/reads/r16_dose01_s${S}_x0.jsonl.gz
  get artifacts/coe/eval/pend_dose01_s${S}_g0.rows.jsonl.gz $D/reads/pend_dose01_s${S}_g0.rows.jsonl.gz
  get artifacts/coe/eval/heldout_dose01_s$S.jsonl $D/reads/heldout_dose01_s$S.jsonl
  for R in $(seq 1 16); do get artifacts/coe/ladder/la_dose01_s$S/mix_$R.jsonl.gz $D/mix/dose01_s${S}_$R.jsonl.gz; done
done
for R in $(seq 24 32); do get artifacts/coe/ladder/la_ko_s1/alloc_$R.json $D/alloc/ko_s1_$R.json; done
for R in $(seq 25 32); do get artifacts/coe/ladder/la_ko_s1/mix_$R.jsonl.gz $D/mix/ko_s1_$R.jsonl.gz; done
get artifacts/coe/eval/r32_ko_s1_x0.jsonl.gz $D/reads/r32_ko_s1_x0.jsonl.gz
echo SMALL DONE
