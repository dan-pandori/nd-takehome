#!/usr/bin/env bash
# round3-run3 ADDENDUM: deep second-seed pass (k = 20,000, sampling seed 1) on the a-priori reachable targets.
# Usage: bash pod/r3_3/deep.sh <reductio|depth3> [seeds...]
cd /workspace/nd-takehome; mkdir -p artifacts/r3_3
SET=$1; shift; SEEDS=${*:-$(seq 30 53)}
case $SET in
  reductio) TAG=reductio_f0;  F=data/r3_3/targets_reductio_deep52.jsonl;;
  depth3)   TAG=depth3_f0_a1; F=data/r3_3/targets_depth3_deep45.jsonl;;
  *) echo "bad set"; exit 1;;
esac
N=$(wc -l < $F)
for s in $SEEDS; do CK=ckpts/r3_3/stage1_${TAG}_s$s.pt; OUT=artifacts/r3_3/deep_${TAG}_s$s
  [ -f "$CK" ] || { echo "MISSING $CK"; continue; }
  if [ -f "$OUT.s0.jsonl" ] && [ "$(wc -l < $OUT.s0.jsonl)" = "$N" ]; then echo "skip deep $s"; continue; fi
  echo "$(date -u +%FT%TZ) deep $TAG s$s start"
  python -u coverage.py --ckpt $CK --in $F --k 20000 --temperature 0.8 --batch 2000 --procs 4 --seed 1 --out $OUT > artifacts/r3_3/deep_${TAG}_s$s.log 2>&1; rc=$?
  echo "$(date -u +%FT%TZ) deep $TAG s$s rc=$rc records $(wc -l < $OUT.s0.jsonl)"
done
echo "$(date -u +%FT%TZ) DEEP DONE $TAG $SEEDS"
