#!/usr/bin/env bash
# Poll until seed S's pod has RUN_DONE_s<S> (or a failure line), at most MAX seconds.  Usage: bash pod/rc6/waitdone.sh <S> [max]
S=$1; MAX=${2:-540}; t0=$(date +%s)
until out=$(podrun rc6-s$S "cd /workspace/nd-takehome; ls artifacts/rc6/RUN_DONE_s$S 2>/dev/null; grep -E 'FAIL' artifacts/rc6/run_s$S.log; tail -n 1 artifacts/rc6/run_s$S.log" 2>/dev/null); grep -qE 'RUN_DONE|FAIL' <<<"$out" || [ $(( $(date +%s) - t0 )) -ge $MAX ]; do sleep 45; done
echo "$out"; date -u +%T
