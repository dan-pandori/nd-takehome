#!/usr/bin/env bash
# Pod setup for create-or-elicit: Lean 4 v4.34.1 core via elan, hf CLI, K12 and K12- from the bucket.
. pod/coe/env.sh
{
  [ -x ~/.elan/bin/lean ] || { curl -sSfL https://raw.githubusercontent.com/leanprover/elan/master/elan-init.sh | sh -s -- -y --default-toolchain leanprover/lean4:v4.34.1; }
  ~/.elan/bin/lean --version
  nproc; nvidia-smi --query-gpu=name,memory.total --format=csv,noheader; python3 -c "import torch; print('torch', torch.__version__)"
  python3 -c "import lean_gate; print('lean cpu quota', lean_gate.cpu_quota())"
  pip -q install --break-system-packages -U 'huggingface_hub[cli]' 2>&1 | tail -1
  mkdir -p data/kh data/coe
  [ -s data/kh/train_k12.jsonl ] || { hf buckets cp $BK/cap-horizon/data/kh/train_k12.jsonl.gz data/kh/train_k12.jsonl.gz && gunzip -f data/kh/train_k12.jsonl.gz; }
  [ -s data/coe/train_k12ko.jsonl ] || { hf buckets cp $BK/create-or-elicit/data/coe/train_k12ko.jsonl.gz data/coe/train_k12ko.jsonl.gz && gunzip -f data/coe/train_k12ko.jsonl.gz; }
  md5sum data/kh/train_k12.jsonl data/coe/train_k12ko.jsonl; wc -l data/kh/train_k12.jsonl data/coe/train_k12ko.jsonl data/coe/*.jsonl data/bs/*.jsonl
  echo SETUP_DONE
} > artifacts/coe/logs/setup_$(hostname).log 2>&1
