# sourced by every rl-from-ckpt pod job
export PATH=$HOME/.elan/bin:$PATH
export OMP_NUM_THREADS=8
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
export LEAN_GATE_WORKERS=${LEAN_GATE_WORKERS:-32}
export ND_SAMPLE_PATH=fast
export ND_RUN_ID=rl-from-ckpt
cd /workspace/nd-takehome
mkdir -p artifacts/rfc/logs artifacts/rfc/eval artifacts/rfc/score ckpts/rfc/ladder ckpts/rfc/control ckpts/tj
BK=hf://buckets/dan-pandori/nd-rl
up() { hf buckets sync "$1" "$BK/rl-from-ckpt/$1" --exclude 'dump/*' --exclude '*.pt' --exclude 'mix_*' >/dev/null 2>&1 || echo "UPLOAD FAILED $1"
       [ -d artifacts/rl-from-ckpt ] && { hf buckets sync artifacts/rl-from-ckpt "$BK/rl-from-ckpt/artifacts/rl-from-ckpt" >/dev/null 2>&1 || echo "UPLOAD FAILED registry"; }; }
# fetch a bucket object (path relative to the nd-rl bucket root) to a local path, retrying until it exists
fetch() { until [ -s "$2" ]; do mkdir -p "$(dirname "$2")"; hf buckets cp "$BK/$1" "$2.part" >/dev/null 2>&1 && mv "$2.part" "$2" || { rm -f "$2.part"; sleep 60; }; done; }
