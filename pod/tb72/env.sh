# sourced by every textbook72 pod job
export PATH=$HOME/.elan/bin:$PATH
export OMP_NUM_THREADS=4
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
Q=$(awk '{if ($1=="max") print 8; else printf "%d", $1/$2}' /sys/fs/cgroup/cpu.max 2>/dev/null || echo 8)
export LEAN_GATE_WORKERS=${LEAN_GATE_WORKERS:-$(( Q > 2 ? Q - 1 : 2 ))}
export ND_SAMPLE_PATH=fast
export ND_RUN_ID=textbook72
cd /workspace/nd-takehome
mkdir -p artifacts/textbook72/logs artifacts/textbook72/eval ckpts/tb72 data/tb72
BK=hf://buckets/dan-pandori/nd-rl
