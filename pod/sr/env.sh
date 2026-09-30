# sourced by every state-readouts pod job
export PATH=$HOME/.elan/bin:$PATH
export OMP_NUM_THREADS=8
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
export LEAN_GATE_WORKERS=${LEAN_GATE_WORKERS:-32}
export ND_SAMPLE_PATH=fast
export ND_RUN_ID=state-readouts
cd /workspace/nd-takehome
mkdir -p artifacts/state-readouts/logs artifacts/state-readouts/dump
