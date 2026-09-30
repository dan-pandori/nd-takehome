# sourced by every search-expert pod job
export PATH=$HOME/.elan/bin:$PATH
export OMP_NUM_THREADS=4
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
export LEAN_GATE_WORKERS=${LEAN_GATE_WORKERS:-16}
export ND_SAMPLE_PATH=fast
export ND_RUN_ID=search-expert
cd /workspace/nd-takehome
mkdir -p artifacts/sx/logs artifacts/sx/dump ckpts/sx/ladder
BK=hf://buckets/dan-pandori/nd-rl/search-expert
up() { hf buckets sync "$1" "$BK/$1" --exclude 'dump/*' >/dev/null 2>&1 || echo "UPLOAD FAILED $1"; }
