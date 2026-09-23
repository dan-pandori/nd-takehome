#!/usr/bin/env bash
# On-pod sequencer. Usage: setsid nohup bash pod/dsr/run_all.sh <arm> > /dev/null 2>&1 &
# Reads pod/dsr/plan_<arm>.txt: "<name><TAB><cmd>" lines; a line that is exactly "--" is a barrier
# (everything before it must finish before anything after it starts). Jobs inside a group run in
# parallel -- the plan never puts more than 2 sampling jobs in one group (efficiency run: >2
# co-tenant sampling jobs per 24 GB GPU is counterproductive).
cd /workspace/nd-takehome
ARM=$1
PLAN=pod/dsr/plan_$ARM.txt
echo "RUN_ALL_START $(date -u +%FT%TZ) $ARM" >> artifacts/dsr/logs/run_all.log
bash pod/dsr/setup.sh "$(head -1 pod/dsr/mode_$ARM.txt)"
pids=()
flush() { for p in "${pids[@]}"; do wait "$p"; done; pids=(); }
while IFS= read -r line; do
  [ -z "$line" ] && continue
  case "$line" in
    '#'*) continue ;;
    '--') flush; echo "BARRIER $(date -u +%FT%TZ)" >> artifacts/dsr/logs/run_all.log; continue ;;
  esac
  name="${line%%	*}"; cmd="${line#*	}"
  echo "LAUNCH $(date -u +%FT%TZ) $name" >> artifacts/dsr/logs/run_all.log
  bash pod/dsr/job.sh "$name" "$cmd" &
  pids+=($!)
done < "$PLAN"
flush
echo "RUN_ALL_DONE $(date -u +%FT%TZ) $ARM" >> artifacts/dsr/logs/run_all.log
touch artifacts/dsr/ARM_DONE
