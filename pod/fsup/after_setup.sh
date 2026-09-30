#!/usr/bin/env bash
# Wait for pod setup, then run a ladder.  Usage: bash pod/fsup/after_setup.sh <arm> <seed>
until grep -q SETUP_DONE /workspace/nd-takehome/artifacts/fsup/setup.log 2>/dev/null; do sleep 20; done
exec bash pod/fsup/ladder.sh "$@"
