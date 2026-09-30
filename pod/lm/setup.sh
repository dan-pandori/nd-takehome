#!/usr/bin/env bash
# lit-measures pod setup: hf CLI, the noise-floor p1 training set, the held-out set; an origin/dan copy of the trainer
# in /workspace/orig for the default-reproduction check (pushed by pod/lm/push_orig.sh).
cd /workspace/nd-takehome; mkdir -p artifacts/lit-measures/m2 data/nf data/p2
{
  [ -x ~/.elan/bin/lean ] || { curl -sSf https://raw.githubusercontent.com/leanprover/elan/master/elan-init.sh | sh -s -- -y --default-toolchain leanprover/lean4:v4.34.0; }
  ~/.elan/bin/lean --version
  nproc; nvidia-smi --query-gpu=name,memory.total --format=csv,noheader
  python3 -c 'import torch; assert torch.cuda.is_available(), "NO CUDA"; print("cuda ok", torch.cuda.get_device_name(0))' || echo CUDA_BROKEN
  pip -q install --break-system-packages -U 'huggingface_hub[cli]' 2>&1 | tail -1
  B=hf://buckets/dan-pandori/nd-rl
  hf buckets cp $B/noise-floor/data/nf/train_p1.jsonl data/nf/train_p1.jsonl
  hf buckets cp $B/lean-format/data/p2/heldout.jsonl data/p2/heldout.jsonl
  md5sum data/nf/train_p1.jsonl data/p2/heldout.jsonl; wc -l data/nf/train_p1.jsonl data/p2/heldout.jsonl
  echo SETUP_DONE
} > artifacts/lit-measures/m2/setup_$(hostname).log 2>&1
