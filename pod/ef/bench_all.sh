#!/usr/bin/env bash
# Run efficiency: the before/after grid, one bench per line, sequentially on one GPU.
# Usage: bash pod/ef/bench_all.sh <listfile>
cd /workspace/nd-takehome
while IFS=$'\t' read -r name args; do
  [ -z "$name" ] && continue
  [ -f artifacts/ef/$name.json ] && { echo "skip $name"; continue; }
  bash pod/ef/job.sh "$name" "python3 bench_sampler.py --tag $name $args"
  echo "done $name"
done < "$1"
touch artifacts/ef/bench_all.done
