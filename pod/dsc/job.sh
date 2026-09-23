#!/usr/bin/env bash
# One job on the pod. Usage: bash pod/dsc/job.sh <jobname> '<command line>'   Log artifacts/dsc/logs/<jobname>.log ; markers artifacts/dsc/<jobname>.done|.failed
cd /workspace/nd-takehome; export CUDA_MEM_FRACTION=${CUDA_MEM_FRACTION:-0.18} PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True LEAN_GATE_WORKERS=${LEAN_GATE_WORKERS:-12} OMP_NUM_THREADS=4 MKL_NUM_THREADS=4 PATH=$HOME/.elan/bin:$PATH
J=$1; shift; mkdir -p artifacts/dsc/logs
export LEAN_GATE_LOG=artifacts/dsc/gate_$J.jsonl
echo "START $(date -u +%FT%TZ) $*" > artifacts/dsc/logs/$J.log
if bash -c "$*" >> artifacts/dsc/logs/$J.log 2>&1; then echo "END $(date -u +%FT%TZ)" >> artifacts/dsc/logs/$J.log; touch artifacts/dsc/$J.done; else echo "FAILED $(date -u +%FT%TZ)" >> artifacts/dsc/logs/$J.log; touch artifacts/dsc/$J.failed; fi
