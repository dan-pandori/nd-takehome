#!/usr/bin/env bash
# Run efficiency, step 6: round time at 1..4 concurrent sampling+gate jobs on one GPU.
# A "round" here is 200 targets x k 128 = 25,600 samples + the Lean gate, the recommended fast config at batch 1024.
cd /workspace/nd-takehome
for n in 1 2 3 4; do
  rm -f artifacts/ef/co_n${n}_*.json
  bash pod/ef/cotenancy.sh $n co --n_targets 200 --k 128 --batch 1024 --max_new 288 \
       --path fast --early eos --compact 1 --rowrng 1 --save_tokens 0
done
touch artifacts/ef/cotenancy.done
