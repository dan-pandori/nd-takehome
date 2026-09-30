#!/usr/bin/env bash
# Pod setup for search-expert: Lean 4.34.0 core, hf CLI, K12 (Stage-1 / replay set), held-out p2, SN-cap12 Stage-1 s0-s3.
# data/ladder is pushed from the VPS (pod/sx/pushdata.sh).
cd /workspace/nd-takehome; mkdir -p artifacts/sx ckpts/sx data/p2 data/kh
{
  [ -x ~/.elan/bin/lean ] || { curl -sSf https://raw.githubusercontent.com/leanprover/elan/master/elan-init.sh | sh -s -- -y --default-toolchain leanprover/lean4:v4.34.0; }
  ~/.elan/bin/lean --version
  nproc; cat /sys/fs/cgroup/cpu.max 2>/dev/null; nvidia-smi --query-gpu=name,memory.total --format=csv,noheader
  pip -q install --break-system-packages -U 'huggingface_hub[cli]' 2>&1 | tail -1
  B=hf://buckets/dan-pandori/nd-rl
  hf buckets cp $B/lean-format/data/p2/heldout.jsonl data/p2/heldout.jsonl
  hf buckets cp $B/cap-horizon/data/kh/train_k12.jsonl.gz data/kh/train_k12.jsonl.gz && gunzip -f data/kh/train_k12.jsonl.gz
  for s in 0 1 2 3; do hf buckets cp $B/state-cap12/ckpts/sc12/stage1_SN12_s$s.pt ckpts/sx/stage1_SN12_s$s.pt; done
  md5sum ckpts/sx/*.pt; wc -l data/p2/*.jsonl data/ladder/rl_targets.jsonl data/kh/*.jsonl
  echo SETUP_DONE
} > artifacts/sx/setup.log 2>&1
