#!/usr/bin/env bash
# One job. Usage: bash pod/dsr/job.sh <jobname> '<command line>'
# Log artifacts/dsr/logs/<jobname>.log ; markers artifacts/dsr/<jobname>.done|.failed
cd /workspace/nd-takehome
export CUDA_MEM_FRACTION=${CUDA_MEM_FRACTION:-0.42} PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
export LEAN_GATE_WORKERS=${LEAN_GATE_WORKERS:-12} OMP_NUM_THREADS=4 MKL_NUM_THREADS=4 PATH=$HOME/.elan/bin:$PATH
J=$1; shift; mkdir -p artifacts/dsr/logs
export LEAN_GATE_LOG=artifacts/dsr/gate_$J.jsonl
[ -f artifacts/dsr/$J.done ] && { echo "skip $J (done)"; exit 0; }
echo "START $(date -u +%FT%TZ) $*" > artifacts/dsr/logs/$J.log
if bash -c "$*" >> artifacts/dsr/logs/$J.log 2>&1; then echo "END $(date -u +%FT%TZ)" >> artifacts/dsr/logs/$J.log; touch artifacts/dsr/$J.done
else echo "FAILED $(date -u +%FT%TZ)" >> artifacts/dsr/logs/$J.log; touch artifacts/dsr/$J.failed; fi
