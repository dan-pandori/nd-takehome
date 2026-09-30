#!/usr/bin/env bash
# Pod setup for state-cap12: Lean 4.34.0 core via elan, hf CLI, the held-out set and the K12 Stage-1 checkpoints from the bucket.
# data/ladder and data/kh/train_k12.jsonl are pushed from the VPS (pod/sc12/pushdata.sh).
cd /workspace/nd-takehome; mkdir -p artifacts/sc12 ckpts/sc12 ckpts/kh data/p2
{
  [ -x ~/.elan/bin/lean ] || { curl -sSf https://raw.githubusercontent.com/leanprover/elan/master/elan-init.sh | sh -s -- -y --default-toolchain leanprover/lean4:v4.34.0; }
  ~/.elan/bin/lean --version
  nproc; nvidia-smi --query-gpu=name,memory.total --format=csv,noheader
  pip -q install --break-system-packages -U 'huggingface_hub[cli]' 2>&1 | tail -1
  B=hf://buckets/dan-pandori/nd-rl
  hf buckets cp $B/lean-format/data/p2/heldout.jsonl data/p2/heldout.jsonl
  for s in 0 1; do hf buckets cp $B/cap-horizon/ckpts/kh/stage1_k12_s$s.pt ckpts/kh/stage1_k12_s$s.pt; done
  wc -l data/p2/*.jsonl data/ladder/*.jsonl data/kh/*.jsonl; ls -la ckpts/kh
  echo SETUP_DONE
} > artifacts/sc12/setup.log 2>&1
