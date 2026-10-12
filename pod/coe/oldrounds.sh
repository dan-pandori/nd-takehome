#!/usr/bin/env bash
# Per-round read-outs (coe/coe_rounds.py) of the OLD full ladders s0-s2: trajectory r1-r8 + rl-continue r9-r16, merged in
# one directory per seed (alloc/round files of both; the last found / found_transfer files from rl-continue).
# Usage: bash pod/coe/oldrounds.sh
source pod/coe/env.sh
for S in 0 1 2; do
  D=artifacts/coe/oldladder/la_T1_best12_s$S; mkdir -p $D
  hf buckets sync $BK/trajectory/artifacts/tj/la_T1_best12_s$S $D --include 'round_*.json' --include 'alloc_*.json' >/dev/null 2>&1
  hf buckets sync $BK/rl-continue/artifacts/rc/la_T1_best12_s$S $D --include 'round_*.json' --include 'alloc_*.json' --include 'found_16.jsonl' --include 'found_transfer_16.jsonl' >/dev/null 2>&1
  ls $D | wc -l; du -sh $D
  python3 coe/coe_rounds.py --dir $D --out artifacts/coe/rounds/old_full_s$S.json > artifacts/coe/rounds/old_full_s$S.md 2>&1
  tail -20 artifacts/coe/rounds/old_full_s$S.md
  rm -f $D/found_16.jsonl $D/found_transfer_16.jsonl
done
up artifacts/coe/rounds
echo OLDROUNDS_DONE
