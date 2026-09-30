#!/usr/bin/env bash
# Contamination check on the pod: download every training / replay set of the scored models, then tb72_contam.py.
. pod/tb72/env.sh
{
  D=data/tb72/train; mkdir -p $D
  hf buckets cp $BK/lean-format/data/p2/train_depth3_f0_a1.jsonl $D/cap6_control.jsonl
  hf buckets cp $BK/cap-horizon/data/kh/train_k12.jsonl.gz $D/k12.jsonl.gz
  S="cap6_control=$D/cap6_control.jsonl k12=$D/k12.jsonl.gz ladder_rl_targets=data/ladder/rl_targets.jsonl old_rl_targets=data/rl_targets.jsonl"
  for run in state-cap12/artifacts/sc12/la_T1_SN12_s0 state-cap12/artifacts/sc12/la_T1_SN12_s1 state-cap12/artifacts/sc12/la_T1_SN12_s2 \
             state-cap12/artifacts/sc12/la_T1_SN12_s3 state-env/artifacts/se/la_T1_SN_s0 state-env/artifacts/se/la_T1_SN_s1; do
    b=$(basename $run)
    for r in 1 2 3 4 5 6 7 8; do
      hf buckets cp $BK/$run/mix_$r.jsonl $D/${b}_mix_$r.jsonl && S="$S ${b}_mix_$r=$D/${b}_mix_$r.jsonl"
    done
  done
  ls -la $D | head -60
  python3 tb72_contam.py --out artifacts/textbook72/contam.json $S
  echo CONTAM_DONE
} > artifacts/textbook72/logs/contam.log 2>&1
