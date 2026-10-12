#!/usr/bin/env bash
# coe-r0 after the 100-theorem reads: re-run the old-ladder per-round analysis with the final coe_rounds.py (broadened sigma
# subtypes), then upload everything.
source pod/coe/env.sh
until [ -e artifacts/coe/markers/oldreads_h100.done ]; do sleep 60; done
bash pod/coe/oldrounds.sh > artifacts/coe/logs/oldrounds_final.log 2>&1
up artifacts/coe/eval; up artifacts/coe/rounds; up artifacts/create-or-elicit
touch artifacts/coe/markers/r0_final.done
echo R0_FINAL_DONE
