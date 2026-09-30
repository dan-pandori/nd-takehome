#!/usr/bin/env bash
# Pod setup for run state-readouts: Lean 4.34.0 (core) via elan, hf CLI, the checkpoints from the public bucket.
cd /workspace/nd-takehome; mkdir -p artifacts/state-readouts ckpts/sr
{
  [ -x ~/.elan/bin/lean ] || { curl -sSf https://raw.githubusercontent.com/leanprover/elan/master/elan-init.sh | sh -s -- -y --default-toolchain leanprover/lean4:v4.34.0; }
  ~/.elan/bin/lean --version
  nproc; nvidia-smi --query-gpu=name,memory.total --format=csv,noheader
  pip -q install --break-system-packages -U 'huggingface_hub[cli]' 2>&1 | tail -1
  B=hf://buckets/dan-pandori/nd-rl
  for s in 0 1; do for m in S SH; do hf buckets cp $B/state-env/ckpts/se/stage1_${m}_s$s.pt ckpts/sr/stage1_${m}_s$s.pt; done; done
  for s in 2 3; do hf buckets cp $B/state-frontier/ckpts/sf2/stage1_S_s$s.pt ckpts/sr/stage1_S_s$s.pt; done
  for s in 0 1 2 3; do
    hf buckets cp $B/state-cap12/ckpts/sc12/stage1_SN12_s$s.pt ckpts/sr/stage1_SN12_s$s.pt
    hf buckets cp $B/state-cap12/ckpts/sc12/ladder/la_T1_SN12_s${s}_r8.pt ckpts/sr/la_T1_SN12_s${s}_r8.pt
  done
  md5sum ckpts/sr/*.pt
  wc -l data/sc/theorems.jsonl data/sc/falsifier_survivors.txt data/sr/*.jsonl
  echo SETUP_DONE
} > artifacts/state-readouts/setup.log 2>&1
