# sourced by every trajectory-cap6 pod job (generated from pod/tj/ by sed: tj->tj6, best12->best6, cap 12->6, K12->p2 cap-6 set)
export PATH=$HOME/.elan/bin:$PATH
export OMP_NUM_THREADS=8
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
export LEAN_GATE_WORKERS=${LEAN_GATE_WORKERS:-32}
export ND_SAMPLE_PATH=fast
export ND_RUN_ID=trajectory-cap6
cd /workspace/nd-takehome
mkdir -p artifacts/tj6/logs artifacts/tj6/dump artifacts/tj6/eval artifacts/tj6/score ckpts/tj6/ladder
BK=hf://buckets/dan-pandori/nd-rl
up() { hf buckets sync "$1" "$BK/trajectory-cap6/$1" --exclude 'dump/*' --exclude '*.pt' >/dev/null 2>&1 || echo "UPLOAD FAILED $1"
       [ "$1" = artifacts/tj6 ] && [ -d artifacts/trajectory-cap6 ] && { hf buckets sync artifacts/trajectory-cap6 "$BK/trajectory-cap6/artifacts/trajectory-cap6" >/dev/null 2>&1 || echo "UPLOAD FAILED registry"; }; }
