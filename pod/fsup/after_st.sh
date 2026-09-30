#!/usr/bin/env bash
# Wait until both Stage-1 jobs (st4, st5) have ended on this pod, then run a ladder.  Usage: bash pod/fsup/after_st.sh <arm> <seed>
cd /workspace/nd-takehome
until { [ -f artifacts/fsup/st4.done ] || [ -f artifacts/fsup/st4.fail ]; } && { [ -f artifacts/fsup/st5.done ] || [ -f artifacts/fsup/st5.fail ]; }; do sleep 30; done
exec bash pod/fsup/ladder.sh "$@"
