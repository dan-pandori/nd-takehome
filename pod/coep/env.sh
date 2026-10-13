# sourced by every create-or-elicit-paper pod job (adapted from pod/coe/env.sh)
export PATH=$HOME/.elan/bin:$PATH
export OMP_NUM_THREADS=8
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
export LEAN_GATE_WORKERS=${LEAN_GATE_WORKERS:-16}
export ND_SAMPLE_PATH=fast
export ND_RUN_ID=create-or-elicit-paper
[ -f pod/coep/GIT_SHA ] && export ND_GIT_SHA=$(cat pod/coep/GIT_SHA)
cd /workspace/nd-takehome
mkdir -p artifacts/coe_paper/eval artifacts/coe_paper/logs ckpts/coe_paper
BK=hf://buckets/dan-pandori/nd-rl
up() { hf buckets sync "$1" "$BK/create-or-elicit-paper/$1" "${@:2}" >/dev/null 2>&1 || echo "UPLOAD FAILED $1"; }
