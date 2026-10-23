# sourced by every style-edl pod job
export PATH=$HOME/.local/bin:$HOME/.elan/bin:$PATH
export OMP_NUM_THREADS=${OMP_NUM_THREADS:-4}
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
export CUBLAS_WORKSPACE_CONFIG=:4096:8
export ND_RUN_ID=style-edl
[ -f pod/sedl/GIT_SHA ] && export ND_GIT_SHA=$(cat pod/sedl/GIT_SHA)
cd /workspace/nd-takehome
mkdir -p artifacts/style_edl/logs artifacts/style_edl/reads ckpts/bs/ladder data/kalmar data/style_edl
BK=hf://buckets/dan-pandori/nd-rl
up() { hf buckets sync "$1" "$BK/style-edl/$1" "${@:2}" >/dev/null 2>&1 || echo "UPLOAD FAILED $1"; }
