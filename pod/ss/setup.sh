#!/usr/bin/env bash
# Pod setup for run support-state: Lean 4.34.0 (core) via elan, the SN checkpoints from the public bucket.
cd /workspace/nd-takehome; mkdir -p artifacts/ss ckpts/se/ladder
{
  [ -x ~/.elan/bin/lean ] || { curl -sSf https://raw.githubusercontent.com/leanprover/elan/master/elan-init.sh | sh -s -- -y --default-toolchain leanprover/lean4:v4.34.0; }
  ~/.elan/bin/lean --version
  nproc; nvidia-smi --query-gpu=name,memory.total --format=csv,noheader
  pip -q install --break-system-packages -U 'huggingface_hub[cli]' 2>&1 | tail -1
  B=hf://buckets/dan-pandori/nd-rl/state-env/ckpts/se
  for s in 0 1; do
    hf buckets cp $B/stage1_SN_s$s.pt ckpts/se/stage1_SN_s$s.pt
    hf buckets cp $B/ladder/la_T1_SN_s${s}_r8.pt ckpts/se/ladder/la_T1_SN_s${s}_r8.pt
  done
  md5sum ckpts/se/*.pt ckpts/se/ladder/*.pt
  wc -l data/sc/theorems.jsonl data/sc/falsifier_survivors.txt
  echo SETUP_DONE
} > artifacts/ss/setup.log 2>&1
