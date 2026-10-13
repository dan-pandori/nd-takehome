#!/usr/bin/env bash
# Per-round analysis of dose seeds whose pods are gone: fetch each ladder's round files and its last found files from the
# bucket into a scratch dir, run coe/coe_rounds.py, keep the JSON, delete the scratch copy.  Usage: bash pod/coe/dose_rounds.sh 1 2
source pod/coe/env.sh > /dev/null 2>&1
mkdir -p artifacts/coe/rounds
for S in "$@"; do
  N=la_dose1_s$S; D=/workspace/scratch/$N; mkdir -p $D
  for f in args.json found_16.jsonl found_transfer_16.jsonl $(seq -f "round_%g.json" 1 16) $(seq -f "alloc_%g.json" 1 16); do
    [ -s $D/$f ] || hf buckets cp $BK/create-or-elicit/artifacts/coe/ladder/$N/$f $D/$f > /dev/null 2>&1 || echo "fetch failed $N/$f"
  done
  nice -n 10 python3 coe/coe_rounds.py --dir $D --out artifacts/coe/rounds/$N.json > artifacts/coe/logs/dose_rounds_$N.log 2>&1 || echo "ROUNDS FAILED $N"
  rm -rf $D
  echo "=== dose_rounds $N $(date -u +%FT%TZ)"
done
up artifacts/coe/rounds
touch artifacts/coe/markers/dose_rounds.done
