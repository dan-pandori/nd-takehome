# sourced by every organism-analysis pod job
export OMP_NUM_THREADS=4
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
export ND_SAMPLE_PATH=fast
export ND_RUN_ID=organism-analysis
cd /workspace/nd-takehome
mkdir -p artifacts/oa/logs artifacts/oa/entropy artifacts/oa/exposure ckpts
BK=hf://buckets/dan-pandori/nd-rl
up() { hf buckets sync "$1" "$BK/organism-analysis/$1" --exclude '*.pt' >/dev/null 2>&1 || echo "UPLOAD FAILED $1"
       [ -d artifacts/organism-analysis ] && { hf buckets sync artifacts/organism-analysis "$BK/organism-analysis/artifacts/organism-analysis" >/dev/null 2>&1 || echo "UPLOAD FAILED registry"; }; }
fetch() { until [ -s "ckpts/$1" ]; do mkdir -p "$(dirname ckpts/$1)"; hf buckets cp "$BK/$1" "ckpts/$1.part" >/dev/null 2>&1 && mv "ckpts/$1.part" "ckpts/$1" || { rm -f "ckpts/$1.part"; sleep 30; }; done; }
