# sourced by every best-state pod job
export PATH=$HOME/.elan/bin:$PATH
export OMP_NUM_THREADS=8
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
export LEAN_GATE_WORKERS=${LEAN_GATE_WORKERS:-32}
export ND_SAMPLE_PATH=fast
export ND_RUN_ID=best-state
cd /workspace/nd-takehome
mkdir -p artifacts/bs/logs artifacts/bs/dump artifacts/bs/eval ckpts/bs/ladder ckpts/inh
BK=hf://buckets/dan-pandori/nd-rl
up() { hf buckets sync "$1" "$BK/best-state/$1" --exclude 'dump/*' >/dev/null 2>&1 || echo "UPLOAD FAILED $1"; }
