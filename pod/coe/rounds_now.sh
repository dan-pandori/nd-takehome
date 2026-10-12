#!/usr/bin/env bash
# Run coe/coe_rounds.py on this pod's ladder directory (latest files) and print the table.  Usage: bash pod/coe/rounds_now.sh
source pod/coe/env.sh > /dev/null 2>&1
mkdir -p artifacts/coe/rounds
for d in artifacts/coe/ladder/la_*; do
  [ -e $d/round_1.json ] || { echo "$(basename $d): no round yet"; continue; }
  python3 coe/coe_rounds.py --dir $d --out artifacts/coe/rounds/$(basename $d).json 2>&1 | tail -20
done
