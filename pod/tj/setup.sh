#!/usr/bin/env bash
# Pod setup for trajectory: Lean 4 v4.34.1 core via elan, hf CLI, the K12 Stage-1 set (trainers) from the bucket.
. pod/tj/env.sh
{
  [ -x ~/.elan/bin/lean ] || { curl -sSfL https://raw.githubusercontent.com/leanprover/elan/master/elan-init.sh | sh -s -- -y --default-toolchain leanprover/lean4:v4.34.1; }
  ~/.elan/bin/lean --version
  nproc; nvidia-smi --query-gpu=name,memory.total --format=csv,noheader; python3 -c "import torch; print('torch', torch.__version__)"
  pip -q install --break-system-packages -U 'huggingface_hub[cli]' 2>&1 | tail -1
  mkdir -p data/kh
  [ "$1" = reader ] || [ -s data/kh/train_k12.jsonl ] || { hf buckets cp $BK/cap-horizon/data/kh/train_k12.jsonl.gz data/kh/train_k12.jsonl.gz && gunzip -f data/kh/train_k12.jsonl.gz; }
  md5sum data/kh/train_k12.jsonl 2>/dev/null; wc -l data/bs/*.jsonl data/tj/*.jsonl 2>/dev/null
  echo SETUP_DONE
} > artifacts/tj/logs/setup_$(hostname).log 2>&1
