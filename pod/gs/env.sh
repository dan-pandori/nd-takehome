# sourced by every grpo-state pod job
export PATH=$HOME/.elan/bin:$PATH
export OMP_NUM_THREADS=8
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
export LEAN_GATE_WORKERS=${LEAN_GATE_WORKERS:-32}
export ND_SAMPLE_PATH=fast
export ND_RUN_ID=grpo-state
cd /workspace/nd-takehome
mkdir -p artifacts/grpo_state/logs ckpts/grpo_state ckpts/sc12
BK=hf://buckets/dan-pandori/nd-rl/grpo-state
up() { hf buckets sync "$1" "$BK/$1" >/dev/null 2>&1 || echo "UPLOAD FAILED $1"; }
