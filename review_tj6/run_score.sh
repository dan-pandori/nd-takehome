#!/bin/sh
# sequential (VPS: one torch process at a time)
R=~/review/trajectory-cap6; P=~/venv-cpu/bin/python; cd $R/review_tj6
for s in 0 1 2; do
  for ck in stage1_best6_s${s}_b1200 stage1_best6_s${s}_b1200_step1600 la_T1_best6_s${s}_r8; do
    $P score.py $R/rv6/ck/$ck.pt $R/artifacts/tj6/targets/targets_s$s.jsonl @$R/rv6/pick_b0_s$s.txt $R/rv6/b0_s${s}_$ck.jsonl b0 > /dev/null
  done
  $P score.py $R/rv6/ck/stage1_best6_s${s}_b1200.pt $R/data/tj6/cross.jsonl @$R/rv6/pick_cross_s$s.txt $R/rv6/b0cross_s${s}_stage1_best6_s${s}_b1200.jsonl b0 > /dev/null
  $P score.py $R/rv6/ck/la_T1_best6_s${s}_r8.pt $R/data/tj6/cross.jsonl @$R/rv6/pick_cross_s$s.txt $R/rv6/b0cross_s${s}_la_T1_best6_s${s}_r8.jsonl b0 > /dev/null
  $P score.py $R/rv6/ck/stage1_best6_s${s}_b1200.pt $R/artifacts/tj6/targets/targets_s$s.jsonl @$R/rv6/pick_full_s$s.txt $R/rv6/full_s${s}_stage1_best6_s${s}_b1200.jsonl > /dev/null
done
echo SCORE_DONE
