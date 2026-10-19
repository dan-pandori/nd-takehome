# sourced by every kalmar-pretrain pod job
export PATH=$HOME/.elan/bin:$HOME/.local/bin:$PATH
export OMP_NUM_THREADS=${OMP_NUM_THREADS:-8}
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
export ND_SAMPLE_PATH=fast
export ND_RUN_ID=kalmar-pretrain
[ -f pod/kal/GIT_SHA ] && export ND_GIT_SHA=$(cat pod/kal/GIT_SHA)
cd /workspace/nd-takehome
mkdir -p artifacts/kalmar/logs artifacts/kalmar/eval artifacts/kalmar/tf artifacts/kalmar/free ckpts/kalmar data/kalmar data/kh
BK=hf://buckets/dan-pandori/nd-rl
up() { hf buckets sync "$1" "$BK/kalmar-pretrain/$1" "${@:2}" >/dev/null 2>&1 || echo "UPLOAD FAILED $1"; }
