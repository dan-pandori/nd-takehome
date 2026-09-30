#!/usr/bin/env bash
# Pod setup: Lean 4.34.0 core via elan, hf CLI, held-out set, K12 train set, SN-cap12 Stage-1 s0-s3 and state-cap12's T1 r8 checkpoints.
# data/ladder is pushed from the VPS (pod/fsup/pushdata.sh).
cd /workspace/nd-takehome; mkdir -p artifacts/fsup ckpts/sc12/ladder data/p2 data/kh
{
  [ -x ~/.elan/bin/lean ] || { curl -sSf https://raw.githubusercontent.com/leanprover/elan/master/elan-init.sh | sh -s -- -y --default-toolchain leanprover/lean4:v4.34.0; }
  ~/.elan/bin/lean --version
  nproc; cat /sys/fs/cgroup/cpu.max 2>/dev/null; nvidia-smi --query-gpu=name,memory.total --format=csv,noheader
  pip -q install --break-system-packages -U 'huggingface_hub[cli]' 2>&1 | tail -1
  B=hf://buckets/dan-pandori/nd-rl
  hf buckets cp $B/lean-format/data/p2/heldout.jsonl data/p2/heldout.jsonl
  [ -s data/kh/train_k12.jsonl ] || { hf buckets cp $B/cap-horizon/data/kh/train_k12.jsonl.gz data/kh/train_k12.jsonl.gz && gunzip -f data/kh/train_k12.jsonl.gz; }
  for s in 0 1 2 3; do
    hf buckets cp $B/state-cap12/ckpts/sc12/stage1_SN12_s$s.pt ckpts/sc12/stage1_SN12_s$s.pt
    hf buckets cp $B/state-cap12/ckpts/sc12/ladder/la_T1_SN12_s${s}_r8.pt ckpts/sc12/ladder/la_T1_SN12_s${s}_r8.pt
  done
  md5sum data/kh/train_k12.jsonl; wc -l data/p2/*.jsonl data/ladder/*.jsonl data/kh/*.jsonl; ls -la ckpts/sc12 ckpts/sc12/ladder
  python3 -c "import torch; print('cuda', torch.cuda.is_available())"
  echo SETUP_DONE
} > artifacts/fsup/setup.log 2>&1
