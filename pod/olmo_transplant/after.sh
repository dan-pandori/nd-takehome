#!/usr/bin/env bash
# after.sh <wait-job> <job-line> [<job-line> ...]: wait for meta/<wait-job>.done and for every requests file a job line
# names, then run the job lines one after another (each a full command, e.g. "bash pod/olmo_transplant/job.sh ...").
# A job whose meta/<job>.done exists is skipped. Run olmo-transplant.
cd /workspace/nd-takehome; A=artifacts/olmo_transplant; W=$1; shift
until [ -f $A/meta/$W.done ]; do sleep 30; done
for L in "$@"; do
  J=$(echo "$L" | awk '{print $3}'); [ -f $A/meta/$J.done ] && continue
  for f in $(echo "$L" | grep -o 'artifacts/olmo_transplant/requests/[^ ]*'); do until [ -f $f ]; do sleep 30; done; done
  echo "AFTER start $J $(date -u +%FT%TZ)"
  bash -c "$L" > $A/logs/q_$J.log 2>&1
  echo "AFTER end $J $(date -u +%FT%TZ) $(grep -o 'JOB_DONE.*' $A/logs/q_$J.log)"
done
echo "AFTER_DONE $(date -u +%FT%TZ)"
