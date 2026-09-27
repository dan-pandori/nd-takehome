#!/usr/bin/env bash
# One job. Usage: bash pod/sd/job.sh <jobname> '<command line>'
# Log artifacts/sd/logs/<jobname>.log ; markers artifacts/sd/<jobname>.done|.failed
cd /workspace/nd-takehome
export CUDA_MEM_FRACTION=${CUDA_MEM_FRACTION:-0.21} PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True \
       LEAN_GATE_WORKERS=${LEAN_GATE_WORKERS:-4} OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 PATH=$HOME/.elan/bin:$PATH
J=$1; shift; mkdir -p artifacts/sd/logs
echo "START $(date -u +%FT%TZ) $*" > artifacts/sd/logs/$J.log
if bash -c "$*" >> artifacts/sd/logs/$J.log 2>&1; then
  echo "END $(date -u +%FT%TZ)" >> artifacts/sd/logs/$J.log; touch artifacts/sd/$J.done
else
  echo "FAILED $(date -u +%FT%TZ)" >> artifacts/sd/logs/$J.log; touch artifacts/sd/$J.failed
fi
