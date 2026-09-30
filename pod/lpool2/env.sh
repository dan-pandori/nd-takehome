# sourced by every long-pool-2 pod job
export PATH=$HOME/.elan/bin:$PATH OMP_NUM_THREADS=1 PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
export LEAN_GATE_WORKERS=${LEAN_GATE_WORKERS:-16} ND_SAMPLE_PATH=fast ND_RUN_ID=long-pool-2
cd /workspace/nd-takehome; mkdir -p artifacts/lpool2/logs data/lp2
BK=hf://buckets/dan-pandori/nd-rl/long-pool-2
up() { hf buckets sync "$1" "$BK/$1" --exclude 'dump/*' >/dev/null 2>&1 || echo "UPLOAD FAILED $1"; }
