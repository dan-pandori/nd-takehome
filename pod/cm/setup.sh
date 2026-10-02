#!/usr/bin/env bash
# Pod setup for compute-match: Lean 4 v4.34.1 core via elan, hf CLI, K12 Stage-1 set from the bucket.
. pod/cm/env.sh
{
  [ -x ~/.elan/bin/lean ] || { curl -sSfL https://raw.githubusercontent.com/leanprover/elan/master/elan-init.sh | sh -s -- -y --default-toolchain leanprover/lean4:v4.34.1; }
  ~/.elan/bin/lean --version
  nproc; nvidia-smi --query-gpu=name,memory.total --format=csv,noheader; python3 -c "import torch; print('torch', torch.__version__)"
  pip -q install --break-system-packages -U 'huggingface_hub[cli]' 2>&1 | tail -1
  mkdir -p data/kh
  [ -s data/kh/train_k12.jsonl ] || { hf buckets cp $BK/cap-horizon/data/kh/train_k12.jsonl.gz data/kh/train_k12.jsonl.gz && gunzip -f data/kh/train_k12.jsonl.gz; }
  md5sum data/kh/train_k12.jsonl; wc -l data/kh/*.jsonl data/bs/*.jsonl data/ladder/*.jsonl
  echo SETUP_DONE
} > artifacts/cm/logs/setup_$(hostname).log 2>&1
