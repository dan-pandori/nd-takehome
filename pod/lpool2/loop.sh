#!/usr/bin/env bash
# Run chunks <prefix>1, <prefix>2, ... (label.sh, W workers, TR tries/worker, seed base+i) until artifacts/lpool2/STOP exists.
# Usage: loop.sh <prefix> <W> <TR> <seedbase>
P=$1; W=$2; TR=$3; SB=$4; i=1
while [ ! -e artifacts/lpool2/STOP ]; do
  bash pod/lpool2/label.sh $P$i $W $TR $((SB+i)) 32 90; up data/lp2; up artifacts/lpool2; i=$((i+1))
done
