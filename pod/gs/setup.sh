#!/usr/bin/env bash
# Pod setup for grpo-state: Lean 4 v4.34.1 core via elan, hf CLI, SN-cap12 Stage-1 s0 from the state-cap12 bucket.
# data/ladder/{rl_targets,transfer}.jsonl and data/p2/heldout.jsonl are pushed from the VPS (pod/gs/push.sh).
cd /workspace/nd-takehome; mkdir -p artifacts/grpo_state/logs ckpts/sc12
{
  [ -x ~/.elan/bin/lean ] || { curl -sSfL https://raw.githubusercontent.com/leanprover/elan/master/elan-init.sh | sh -s -- -y --default-toolchain leanprover/lean4:v4.34.1; }
  ~/.elan/bin/lean --version
  nproc; cat /sys/fs/cgroup/cpu.max 2>/dev/null; nvidia-smi --query-gpu=name,memory.total --format=csv,noheader
  pip -q install --break-system-packages -U 'huggingface_hub[cli]' 2>&1 | tail -1
  hf buckets cp hf://buckets/dan-pandori/nd-rl/state-cap12/ckpts/sc12/stage1_SN12_s0.pt ckpts/sc12/stage1_SN12_s0.pt
  ls -la ckpts/sc12; wc -l data/ladder/*.jsonl data/p2/*.jsonl
  echo SETUP_DONE
} > artifacts/grpo_state/logs/setup.log 2>&1
