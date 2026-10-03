#!/usr/bin/env bash
# Pod setup: Lean 4 v4.34.1 core, hf CLI, K12 (replay set), and trajectory's r8 state for seed S at the resume paths.
# Usage: bash pod/rc/setup.sh <seed>
. pod/rc/env.sh
S=$1; N=la_T1_best12_s$S
{
  [ -x ~/.elan/bin/lean ] || { curl -sSfL https://raw.githubusercontent.com/leanprover/elan/master/elan-init.sh | sh -s -- -y --default-toolchain leanprover/lean4:v4.34.1; }
  ~/.elan/bin/lean --version
  nproc; nvidia-smi --query-gpu=name,memory.total --format=csv,noheader; python3 -c "import torch; print('torch', torch.__version__)"
  pip -q install --break-system-packages -U 'huggingface_hub[cli]' 2>&1 | tail -1
  mkdir -p data/kh artifacts/rc/$N
  [ -s data/kh/train_k12.jsonl ] || { hf buckets cp $BK/cap-horizon/data/kh/train_k12.jsonl.gz data/kh/train_k12.jsonl.gz && gunzip -f data/kh/train_k12.jsonl.gz; }
  for f in found_8.jsonl found_transfer_8.jsonl alloc_8.json round_8.json; do
    [ -s artifacts/rc/$N/$f ] || hf buckets cp $BK/trajectory/artifacts/tj/$N/$f artifacts/rc/$N/$f; done
  [ -s ckpts/rc/ladder/${N}_r8.pt ] || hf buckets cp $BK/trajectory/ckpts/tj/ladder/${N}_r8.pt ckpts/rc/ladder/${N}_r8.pt
  md5sum data/kh/train_k12.jsonl ckpts/rc/ladder/${N}_r8.pt artifacts/rc/$N/*_8.json*; wc -l artifacts/rc/$N/found_8.jsonl artifacts/rc/$N/found_transfer_8.jsonl
  echo SETUP_DONE
} > artifacts/rc/logs/setup_s$S.log 2>&1
