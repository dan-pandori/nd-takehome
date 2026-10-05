# sourced by every capability-defs pod job
export PATH=$HOME/.elan/bin:$HOME/.local/bin:$PATH
export OMP_NUM_THREADS=8
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
export LEAN_GATE_WORKERS=${LEAN_GATE_WORKERS:-32}
export ND_SAMPLE_PATH=fast
export ND_RUN_ID=capability-defs
cd /workspace/nd-takehome
mkdir -p artifacts/cd/logs artifacts/cd/j1 artifacts/cd/j2 artifacts/cd/j3 artifacts/cd/j4 ckpts/cd/j4
BK=hf://buckets/dan-pandori/nd-rl
CK=ckpts/cd
