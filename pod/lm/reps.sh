#!/usr/bin/env bash
# Amendment 1 (2026-09-30, before any grid result was read): 8 re-runs of cell i0_d100 with identical seeds, to measure
# the variance that GPU non-determinism alone produces (the 300-step repro runs diverge after ~step 20 at fixed seeds).
for R in r1 r2 r3 r4 r5 r6 r7 r8; do bash pod/lm/cell.sh 0 100 $R || echo "CELL FAILED i0 d100 $R"; done
echo REPS_DONE
