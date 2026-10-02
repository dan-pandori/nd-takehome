# sourced by every mcts-a pod job
export PATH=$HOME/.elan/bin:$PATH
export OMP_NUM_THREADS=8
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
export LEAN_GATE_WORKERS=${LEAN_GATE_WORKERS:-32}
export ND_SAMPLE_PATH=fast
export ND_RUN_ID=mcts-a
cd /workspace/nd-takehome
mkdir -p artifacts/mcts/logs artifacts/mcts/eval artifacts/mcts/vdata artifacts/mcts/value ckpts/mcts
BK=hf://buckets/dan-pandori/nd-rl
up() { hf buckets sync "$1" "$BK/mcts-a/$1" >/dev/null 2>&1 || echo "UPLOAD FAILED $1"; }
ts() { date -u +%FT%TZ; }
