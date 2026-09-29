# sourced by every state-cap12 pod job
export PATH=$HOME/.elan/bin:$PATH
export OMP_NUM_THREADS=8
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
export LEAN_GATE_WORKERS=${LEAN_GATE_WORKERS:-32}
export ND_SAMPLE_PATH=fast
export ND_RUN_ID=state-cap12
cd /workspace/nd-takehome
mkdir -p artifacts/sc12/logs artifacts/sc12/dump ckpts/sc12/ladder
BK=hf://buckets/dan-pandori/nd-rl/state-cap12
up() { hf buckets sync "$1" "$BK/$1" --exclude 'dump/*' >/dev/null 2>&1 || echo "UPLOAD FAILED $1"; }
