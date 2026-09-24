#!/usr/bin/env bash
# One job on the pod. Usage: bash pod/kh/job.sh <jobname> '<command line>'   Log artifacts/kh/logs/<jobname>.log ; markers artifacts/kh/<jobname>.done|.failed
cd /workspace/nd-takehome; export CUDA_MEM_FRACTION=${CUDA_MEM_FRACTION:-0.18} PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True LEAN_GATE_WORKERS=${LEAN_GATE_WORKERS:-12} OMP_NUM_THREADS=4 MKL_NUM_THREADS=4 PATH=$HOME/.elan/bin:$PATH
J=$1; shift; mkdir -p artifacts/kh/logs
export LEAN_GATE_LOG=artifacts/kh/gate_$J.jsonl
echo "START $(date -u +%FT%TZ) $*" > artifacts/kh/logs/$J.log
if bash -c "$*" >> artifacts/kh/logs/$J.log 2>&1; then echo "END $(date -u +%FT%TZ)" >> artifacts/kh/logs/$J.log; touch artifacts/kh/$J.done; else echo "FAILED $(date -u +%FT%TZ)" >> artifacts/kh/logs/$J.log; touch artifacts/kh/$J.failed; fi
