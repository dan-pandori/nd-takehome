# sourced by every state-frontier pod job (from pod/se/env.sh; + LEAN_GATE_DUMP per job, set by bg.sh)
export PATH=$HOME/.elan/bin:$PATH
export OMP_NUM_THREADS=8
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
export LEAN_GATE_WORKERS=${LEAN_GATE_WORKERS:-32}
export ND_SAMPLE_PATH=fast
cd /workspace/nd-takehome
mkdir -p artifacts/sf2/logs artifacts/sf2/dumps ckpts/sf2/ladder
BK=hf://buckets/dan-pandori/nd-rl/state-frontier
up() { hf buckets sync "$1" "$BK/$1" >/dev/null 2>&1 || echo "UPLOAD FAILED $1"; }
