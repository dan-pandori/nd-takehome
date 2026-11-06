#!/usr/bin/env bash
# start.sh <job> ...: pod set-up (once), then the job queue (pod/olmo_iffu/runq.sh).
cd /workspace/nd-takehome; A=artifacts/olmo_iffu; mkdir -p $A/logs
[ -f $A/meta/setup.done ] || { bash pod/olmo_iffu/setup.sh > $A/logs/setup.log 2>&1; grep -q SETUP_DONE $A/logs/setup.log && { mkdir -p $A/meta; touch $A/meta/setup.done; }; }
[ -f $A/meta/setup.done ] || { echo "SETUP_FAILED $(date -u +%FT%TZ)"; exit 1; }
bash pod/olmo_iffu/runq.sh "$@"
