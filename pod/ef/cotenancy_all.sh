#!/usr/bin/env bash
cd /workspace/nd-takehome
for n in 1 2 3 4; do
  rm -f artifacts/ef/co_n${n}_*.json
  bash pod/ef/cotenancy.sh $n co --n_targets 50 --k 64 --batch 1024 --path "${CO_PATH:-fast}" --early "${CO_EARLY:-goal}" --rowrng 1 --save_tokens 0
done
touch artifacts/ef/cotenancy.done
