# sourced by every create-or-elicit pod job
export PATH=$HOME/.elan/bin:$PATH
export OMP_NUM_THREADS=8
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
export LEAN_GATE_WORKERS=${LEAN_GATE_WORKERS:-32}
export ND_SAMPLE_PATH=fast
export ND_RUN_ID=create-or-elicit
[ -f pod/coe/GIT_SHA ] && export ND_GIT_SHA=$(cat pod/coe/GIT_SHA)
cd /workspace/nd-takehome
mkdir -p artifacts/coe/logs artifacts/coe/dump artifacts/coe/eval artifacts/coe/large artifacts/coe/markers artifacts/coe/ladder ckpts/coe/ladder
BK=hf://buckets/dan-pandori/nd-rl
up() { hf buckets sync "$1" "$BK/create-or-elicit/$1" --exclude 'dump/*' "${@:2}" >/dev/null 2>&1 || echo "UPLOAD FAILED $1"; }
