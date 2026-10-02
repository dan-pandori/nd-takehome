# sourced by every grpo-best pod job
export PATH=$HOME/.elan/bin:$PATH
export OMP_NUM_THREADS=8
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
export LEAN_GATE_WORKERS=${LEAN_GATE_WORKERS:-32}
export ND_SAMPLE_PATH=fast
export ND_RUN_ID=grpo-best
cd /workspace/nd-takehome
mkdir -p artifacts/gb/logs artifacts/gb/eval ckpts/gb ckpts/tj/ladder
BK=hf://buckets/dan-pandori/nd-rl
up() { hf buckets sync "$1" "$BK/grpo-best/$1" --exclude 'dump/*' --exclude '*.pt' --exclude 'found_*.jsonl' >/dev/null 2>&1 || echo "UPLOAD FAILED $1"
       [ -d artifacts/grpo-best ] && { hf buckets sync artifacts/grpo-best "$BK/grpo-best/artifacts/grpo-best" >/dev/null 2>&1 || echo "UPLOAD FAILED registry"; }; }
# fetch a bucket file if missing: get <bucket relpath> <local path>
get() { [ -s "$2" ] || { mkdir -p "$(dirname "$2")"; hf buckets cp "$BK/$1" "$2.part" >/dev/null 2>&1 && mv "$2.part" "$2"; }; [ -s "$2" ]; }
