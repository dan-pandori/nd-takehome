# sourced by every rl-continue-cap6 pod job (rl-continue's pod/rc/env.sh with this run's id and directories)
export PATH=$HOME/.elan/bin:$PATH
export OMP_NUM_THREADS=8
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
export LEAN_GATE_WORKERS=${LEAN_GATE_WORKERS:-32}
export ND_SAMPLE_PATH=fast
export ND_RUN_ID=rl-continue-cap6
cd /workspace/nd-takehome
mkdir -p artifacts/rc6/logs/read artifacts/rc6/eval ckpts/rc6/ladder
BK=hf://buckets/dan-pandori/nd-rl
up() { hf buckets sync "$1" "$BK/rl-continue-cap6/$1" --exclude 'dump/*' --exclude '*.pt' >/dev/null 2>&1 || echo "UPLOAD FAILED $1"
       [ -d artifacts/rl-continue-cap6 ] && { hf buckets sync artifacts/rl-continue-cap6 "$BK/rl-continue-cap6/artifacts/rl-continue-cap6" >/dev/null 2>&1 || echo "UPLOAD FAILED registry"; }; }
