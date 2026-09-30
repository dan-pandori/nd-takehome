#!/usr/bin/env bash
# The 12 read-outs in sequence (restartable: a checkpoint whose summary exists is skipped). Usage: pod/tb72/eval.sh [ckpt names]
. pod/tb72/env.sh
L=${*:-"T1_SN12_s0 Fz_SN12_s0 T1_SN12_s1 Fz_SN12_s1 T1_SN12_s2 Fz_SN12_s2 T1_SN12_s3 Fz_SN12_s3 T1_SN6_s0 Fz_SN6_s0 T1_SN6_s1 Fz_SN6_s1"}
for c in $L; do
  O=artifacts/textbook72/eval/$c
  [ -f $O.json ] && { echo "skip $c"; continue; }
  echo "START $c $(date -u +%FT%TZ)"
  ND_ARM=${c%_s*} ND_SEED=${c##*_s} python3 state_eval.py --ckpt ckpts/tb72/$c.pt --in data/tb72/all72.jsonl --out $O.jsonl.tmp --summary $O.json.tmp \
    --k 256 --temperature 0.8 --seed 0 --batch ${TB_BATCH:-4096} --max_action 512 --max_steps 96 --lenfield reference_lines \
    > artifacts/textbook72/logs/$c.log 2>&1 || { echo "FAIL $c"; continue; }
  mv $O.jsonl.tmp $O.jsonl; mv $O.json.tmp $O.json
  echo "END $c $(date -u +%FT%TZ) $(grep SOLVED artifacts/textbook72/logs/$c.log | head -1)"
done
echo QUEUE DONE
