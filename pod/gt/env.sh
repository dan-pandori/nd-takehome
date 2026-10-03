# sourced by every guided-tts pod job
export PATH=$HOME/.elan/bin:$PATH
export OMP_NUM_THREADS=8
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
export LEAN_GATE_WORKERS=${LEAN_GATE_WORKERS:-32}
export ND_SAMPLE_PATH=fast
export ND_RUN_ID=guided-tts
cd /workspace/nd-takehome
mkdir -p artifacts/gt/logs artifacts/gt/eval ckpts/gt
BK=hf://buckets/dan-pandori/nd-rl
SETS=data/gt/tb72_textbook_dev.jsonl,data/gt/tb72_textbook_train.jsonl,data/gt/candidate_v0.jsonl,data/gt/candidate_v1.jsonl,data/gt/batch3.jsonl,data/gt/hand_proved_14.jsonl
