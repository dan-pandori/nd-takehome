#!/usr/bin/env bash
# Pod setup for trajectory-cap6: Lean 4 v4.34.1 core via elan, hf CLI, the cap-6 Stage-1 set (state-env p2 train_depth3_f0_a1, 155,000 records) (trainers) from the bucket.
. pod/tj6/env.sh
{
  [ -x ~/.elan/bin/lean ] || { curl -sSfL https://raw.githubusercontent.com/leanprover/elan/master/elan-init.sh | sh -s -- -y --default-toolchain leanprover/lean4:v4.34.1; }
  ~/.elan/bin/lean --version
  nproc; nvidia-smi --query-gpu=name,memory.total --format=csv,noheader; python3 -c "import torch; print('torch', torch.__version__)"
  pip -q install --break-system-packages -U 'huggingface_hub[cli]' 2>&1 | tail -1
  mkdir -p data/kh
  [ "$1" = reader ] || [ -s data/p2/train_depth3_f0_a1.jsonl ] || { hf buckets cp $BK/state-env/data/p2/train_depth3_f0_a1.jsonl data/p2/train_depth3_f0_a1.jsonl; }
  md5sum data/p2/train_depth3_f0_a1.jsonl 2>/dev/null; wc -l data/bs/*.jsonl data/tj6/*.jsonl 2>/dev/null
  echo SETUP_DONE
} > artifacts/tj6/logs/setup_$(hostname).log 2>&1
