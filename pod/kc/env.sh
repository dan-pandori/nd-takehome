# sourced by every kalmar-complexity pod job
export PATH=$HOME/.local/bin:$PATH
export OMP_NUM_THREADS=${OMP_NUM_THREADS:-4}
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
export ND_RUN_ID=kalmar-complexity
[ -f pod/kc/GIT_SHA ] && export ND_GIT_SHA=$(cat pod/kc/GIT_SHA)
cd /workspace/nd-takehome
mkdir -p artifacts/kc/logs artifacts/kc/b2 ckpts/kc_src data/kalmar data/kh data/kc
BK=hf://buckets/dan-pandori/nd-rl
up() { hf buckets sync "$1" "$BK/kalmar-complexity/$1" "${@:2}" >/dev/null 2>&1 || echo "UPLOAD FAILED $1"; }
