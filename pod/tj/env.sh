# sourced by every trajectory pod job
export PATH=$HOME/.elan/bin:$PATH
export OMP_NUM_THREADS=8
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
export LEAN_GATE_WORKERS=${LEAN_GATE_WORKERS:-32}
export ND_SAMPLE_PATH=fast
export ND_RUN_ID=trajectory
cd /workspace/nd-takehome
mkdir -p artifacts/tj/logs artifacts/tj/dump artifacts/tj/eval artifacts/tj/score ckpts/tj/ladder
BK=hf://buckets/dan-pandori/nd-rl
up() { hf buckets sync "$1" "$BK/trajectory/$1" --exclude 'dump/*' --exclude '*.pt' >/dev/null 2>&1 || echo "UPLOAD FAILED $1"
       [ "$1" = artifacts/tj ] && [ -d artifacts/trajectory ] && { hf buckets sync artifacts/trajectory "$BK/trajectory/artifacts/trajectory" >/dev/null 2>&1 || echo "UPLOAD FAILED registry"; }; }
