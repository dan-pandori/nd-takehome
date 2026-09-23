#!/usr/bin/env bash
# Runs ON the pod, detached, from the moment the arm is launched: waits for the plan to finish, then runs the
# checker of record and uploads this pod's artifacts to the bucket itself.  The executor's host is then not on the
# critical path -- if the driving session is paused, the run still lands its results.
# Usage: setsid nohup bash pod/dsr/finish.sh <arm> <podname> > /dev/null 2>&1 &
cd /workspace/nd-takehome
ARM=$1; POD=$2
export PATH=$HOME/.elan/bin:$PATH LEAN_GATE_WORKERS=${LEAN_GATE_WORKERS:-12}
{
  echo "FINISH_WAIT $(date -u +%FT%TZ) $ARM"
  until [ -f artifacts/dsr/ARM_DONE ]; do sleep 60; done
  echo "FINISH_PLAN_DONE $(date -u +%FT%TZ)"
  python3 pod/dsr/record.py "$ARM" || echo "record.py failed"
  echo "FINISH_RECORDED $(date -u +%FT%TZ)"
  command -v hf >/dev/null && hf buckets sync artifacts/dsr "hf://buckets/dan-pandori/nd-rl/ds-rendering/artifacts/$POD" || echo "NO POD-SIDE UPLOAD (hf absent on the pod image) -- the host does it via dsr_upload.sh"
  echo "FINISH_UPLOADED $(date -u +%FT%TZ)"
  touch artifacts/dsr/FINISH_DONE
} > artifacts/dsr/logs/finish.log 2>&1
