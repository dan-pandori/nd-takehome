#!/usr/bin/env bash
# Pod setup for kalmar-pretrain: Lean 4 v4.34.1 core via elan, hf CLI, the K12-Kalmár training set from the bucket.
. pod/kal/env.sh
{
  [ -x ~/.elan/bin/lean ] || { curl -sSfL https://raw.githubusercontent.com/leanprover/elan/master/elan-init.sh | sh -s -- -y --default-toolchain leanprover/lean4:v4.34.1; }
  ~/.elan/bin/lean --version
  nproc; nvidia-smi --query-gpu=name,memory.total --format=csv,noheader; free -g | head -2; df -h /workspace | tail -1
  python3 -c "import torch; print('torch', torch.__version__)"
  python3 -c "import lean_gate; print('lean cpu quota', lean_gate.cpu_quota())"
  pip -q install --break-system-packages -U 'huggingface_hub[cli]' 2>&1 | tail -1
  [ -s data/kalmar/train_kal_sl.jsonl ] || { hf buckets cp $BK/kalmar-pretrain/data/kalmar/train_kal_sl.jsonl.gz data/kalmar/train_kal_sl.jsonl.gz && gunzip -f data/kalmar/train_kal_sl.jsonl.gz; }
  md5sum data/kalmar/train_kal_sl.jsonl; wc -l data/kalmar/*.jsonl
  echo SETUP_DONE
} > artifacts/kalmar/logs/setup_$(hostname).log 2>&1
