#!/usr/bin/env bash
# Poll the three pods until every seed has finished round R (or anything failed), at most MAX seconds; then print status.
# Usage: bash pod/rc6/wait.sh <round> [max_secs]
R=$1; MAX=${2:-570}; t0=$(date +%s)
chk() { for s in ${SEEDS:-0 1 2}; do podrun rc6-s$s "cd /workspace/nd-takehome; [ -s artifacts/rc6/la_T1_best6_s$s/round_$R.json ] && echo DONE; grep -lE 'FAIL|Traceback' artifacts/rc6/run_s$s.log artifacts/rc6/logs/ladder_s$s.log 2>/dev/null | sed 's/^/ERR /'" 2>/dev/null; done; }
until out=$(chk); [ "$(grep -c DONE <<<"$out")" -ge $(wc -w <<<"${SEEDS:-0 1 2}") ] || grep -q ERR <<<"$out" || [ $(( $(date +%s) - t0 )) -ge $MAX ]; do sleep 60; done
echo "$out" | grep ERR; bash pod/rc6/st.sh
