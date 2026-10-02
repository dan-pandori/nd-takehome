#!/usr/bin/env bash
# Pod setup for grpo-best: Lean 4 v4.34.1 core via elan, hf CLI, trajectory's three base checkpoints.
. pod/gb/env.sh
{
  [ -x ~/.elan/bin/lean ] || { curl -sSfL https://raw.githubusercontent.com/leanprover/elan/master/elan-init.sh | sh -s -- -y --default-toolchain leanprover/lean4:v4.34.1; }
  ~/.elan/bin/lean --version
  nproc; nvidia-smi --query-gpu=name,memory.total --format=csv,noheader; python3 -c "import torch; print('torch', torch.__version__)"
  pip -q install --break-system-packages -U 'huggingface_hub[cli]' 2>&1 | tail -1
  for S in 0 1 2; do get trajectory/ckpts/tj/stage1_best12_s${S}_b1200.pt ckpts/tj/stage1_best12_s${S}_b1200.pt || echo "FETCH FAILED s$S"; done
  md5sum ckpts/tj/*.pt; wc -l data/bs/*.jsonl data/ladder/*.jsonl data/p2/heldout.jsonl
  echo SETUP_DONE
} > artifacts/gb/logs/setup_$(hostname).log 2>&1
