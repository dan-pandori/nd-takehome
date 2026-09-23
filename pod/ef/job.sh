#!/usr/bin/env bash
# One job. Usage: bash pod/ef/job.sh <jobname> '<command line>'  Log artifacts/ef/logs/<jobname>.log ; markers artifacts/ef/<jobname>.done|.failed
cd /workspace/nd-takehome; export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True OMP_NUM_THREADS=${OMP_NUM_THREADS:-8} MKL_NUM_THREADS=${MKL_NUM_THREADS:-8} LEAN_CHECK_WORKERS=${LEAN_CHECK_WORKERS:-64} LEAN_CHECK_CHUNK=${LEAN_CHECK_CHUNK:-300} PATH=$HOME/.elan/bin:$PATH
J=$1; shift; mkdir -p artifacts/ef/logs
export LEAN_GATE_LOG=artifacts/ef/gate_$J.jsonl
rm -f artifacts/ef/$J.done artifacts/ef/$J.failed
echo "START $(date -u +%FT%TZ) $*" > artifacts/ef/logs/$J.log
if bash -c "$*" >> artifacts/ef/logs/$J.log 2>&1; then echo "END $(date -u +%FT%TZ)" >> artifacts/ef/logs/$J.log; touch artifacts/ef/$J.done; else echo "FAILED $(date -u +%FT%TZ)" >> artifacts/ef/logs/$J.log; touch artifacts/ef/$J.failed; fi
