# sourced by every compute-match pod job
export PATH=$HOME/.elan/bin:$PATH
export OMP_NUM_THREADS=8
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
export LEAN_GATE_WORKERS=${LEAN_GATE_WORKERS:-32}
export ND_SAMPLE_PATH=fast
export ND_RUN_ID=compute-match
cd /workspace/nd-takehome
mkdir -p artifacts/cm/logs artifacts/cm/dump artifacts/cm/eval ckpts/cm/ladder ckpts/inh
BK=hf://buckets/dan-pandori/nd-rl
up() { hf buckets sync "$1" "$BK/compute-match/$1" --exclude 'dump/*' >/dev/null 2>&1 || echo "UPLOAD FAILED $1"; }
