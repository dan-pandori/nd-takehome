# sourced by every rl-continue pod job (pod/tj/env.sh with this run's id and directories)
export PATH=$HOME/.elan/bin:$PATH
export OMP_NUM_THREADS=8
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
export LEAN_GATE_WORKERS=${LEAN_GATE_WORKERS:-32}
export ND_SAMPLE_PATH=fast
export ND_RUN_ID=rl-continue
cd /workspace/nd-takehome
mkdir -p artifacts/rc/logs/read artifacts/rc/eval ckpts/rc/ladder
BK=hf://buckets/dan-pandori/nd-rl
up() { hf buckets sync "$1" "$BK/rl-continue/$1" --exclude 'dump/*' --exclude '*.pt' >/dev/null 2>&1 || echo "UPLOAD FAILED $1"
       [ -d artifacts/rl-continue ] && { hf buckets sync artifacts/rl-continue "$BK/rl-continue/artifacts/rl-continue" >/dev/null 2>&1 || echo "UPLOAD FAILED registry"; }; }
