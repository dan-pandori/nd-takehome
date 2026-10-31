# sourced by every coe-dose01 pod job: pod/coe/env.sh with this run's id and bucket path (never create-or-elicit's)
export PATH=$HOME/.elan/bin:$PATH
export OMP_NUM_THREADS=8
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
export LEAN_GATE_WORKERS=${LEAN_GATE_WORKERS:-32}
export ND_SAMPLE_PATH=fast
export ND_RUN_ID=coe-dose01
[ -f pod/d01/GIT_SHA ] && export ND_GIT_SHA=$(cat pod/d01/GIT_SHA)
cd /workspace/nd-takehome
mkdir -p artifacts/coe/logs artifacts/coe/dump artifacts/coe/eval artifacts/coe/markers artifacts/coe/ladder artifacts/coe/rounds ckpts/coe/ladder
BK=hf://buckets/dan-pandori/nd-rl
up() { hf buckets sync "$1" "$BK/coe-dose01/$1" --exclude 'dump/*' "${@:2}" >/dev/null 2>&1 || echo "UPLOAD FAILED $1"; }
