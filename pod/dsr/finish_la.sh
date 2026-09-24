#!/usr/bin/env bash
# Runs ON the pod, detached. For the four arms whose la_frz was cut for budget (log.md 2026-09-24 00:20),
# ARM_DONE will never be touched, so finish.sh's trigger never fires. This waits for la_T1 to finish instead
# -- round_8.json present for BOTH seeds -- then runs the checker of record, so the pod can be deleted as soon
# as the host has pulled it.
# Usage: setsid nohup bash pod/dsr/finish_la.sh <arm> > /dev/null 2>&1 &
cd /workspace/nd-takehome
ARM=$1
export PATH=$HOME/.elan/bin:$PATH LEAN_GATE_WORKERS=${LEAN_GATE_WORKERS:-12}
{
  echo "FINISH_LA_WAIT $(date -u +%FT%TZ) $ARM"
  until [ -f "artifacts/dsr/la_T1_${ARM}_s0/round_8.json" ] && [ -f "artifacts/dsr/la_T1_${ARM}_s1/round_8.json" ]; do
    sleep 60
  done
  echo "FINISH_LA_T1_DONE $(date -u +%FT%TZ)"
  python3 pod/dsr/record.py "$ARM" || echo "record.py failed"
  echo "FINISH_LA_RECORDED $(date -u +%FT%TZ)"
  touch artifacts/dsr/LA_T1_RECORDED
} > artifacts/dsr/logs/finish_la.log 2>&1
