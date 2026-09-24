#!/usr/bin/env bash
# Pod-side scheduler (cap-horizon, 2026-09-23 resume): run the jobs of pod/kh/queue.txt in order, at most N at a time.
# Replaces the AFTER-marker chains of the first session, whose `until ...; do sleep` wrappers survived a kill and
# re-launched their job (log.md 09:25 incident). One process tree per pod: kill this script's process group to stop
# everything. Usage (on the pod):  N=3 setsid nohup bash pod/kh/runner.sh > artifacts/kh/logs/runner.log 2>&1 &
cd /workspace/nd-takehome
N=${N:-3}
Q=${Q:-pod/kh/queue.txt}
echo $$ > artifacts/kh/runner.pid
echo "RUNNER START $(date -u +%FT%TZ) N=$N queue=$Q"
while IFS=$'\t' read -r name cmd; do
  [ -z "$name" ] && continue
  case "$name" in \#*) continue;; esac
  if [ -f artifacts/kh/$name.done ]; then echo "skip $name (done)"; continue; fi
  # also skip a job that another runner already started (job.sh writes the log at START): lets this script be
  # restarted with a different N without ever duplicating a running job (the 2026-09-22 orphan incident)
  if [ -f artifacts/kh/logs/$name.log ]; then echo "skip $name (log exists)"; continue; fi
  # count every job.sh on the pod, not only this shell's children, so a restarted runner respects the same cap
  while [ "$(pgrep -fc 'pod/kh/job[.]sh')" -ge "$N" ]; do sleep 20; done
  echo "launch $(date -u +%FT%TZ) $name"
  bash pod/kh/job.sh "$name" "$cmd" &
  sleep 5
done < "$Q"
wait
rm -f artifacts/kh/runner.pid
echo "RUNNER DONE $(date -u +%FT%TZ)"
