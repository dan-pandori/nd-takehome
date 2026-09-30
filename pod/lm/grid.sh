#!/usr/bin/env bash
# M2 grid, one GPU job at a time.  Usage: bash pod/lm/grid.sh <parity 0|1>  -- cells with (i + d) % 2 == parity, so
# neither factor is aligned with the pod.  init seeds 0-7, data seeds 100-107.
P=$1
for I in 0 1 2 3 4 5 6 7; do for D in 100 101 102 103 104 105 106 107; do
  [ $(( (I + D) % 2 )) -eq $P ] || continue
  bash pod/lm/cell.sh $I $D || echo "CELL FAILED i$I d$D"
done; done
echo GRID_DONE
