#!/usr/bin/env bash
# Pod setup for mcts-a: Lean 4 v4.34.1 core via elan, hf CLI, the K12 generator pool from the bucket.
. pod/mcts/env.sh
{
  [ -x ~/.elan/bin/lean ] || { curl -sSfL https://raw.githubusercontent.com/leanprover/elan/master/elan-init.sh | sh -s -- -y --default-toolchain leanprover/lean4:v4.34.1; }
  ~/.elan/bin/lean --version
  nproc; cat /sys/fs/cgroup/cpu.max 2>/dev/null; nvidia-smi --query-gpu=name,memory.total --format=csv,noheader; python3 -c "import torch; print('torch', torch.__version__)"
  pip -q install --break-system-packages -U 'huggingface_hub[cli]' 2>&1 | tail -1
  mkdir -p data/kh
  [ -s data/kh/train_k12.jsonl ] || { hf buckets cp $BK/cap-horizon/data/kh/train_k12.jsonl.gz data/kh/train_k12.jsonl.gz && gunzip -f data/kh/train_k12.jsonl.gz; }
  md5sum data/kh/train_k12.jsonl; head -c 300 data/kh/train_k12.jsonl; echo
  for S in ${SEEDS:-0 1 2}; do
    [ -s ckpts/mcts/stage1_best12_s${S}_b1200.pt ] || hf buckets cp $BK/trajectory/ckpts/tj/stage1_best12_s${S}_b1200.pt ckpts/mcts/
    [ -s ckpts/mcts/la_T1_best12_s${S}_r8.pt ] || hf buckets cp $BK/trajectory/ckpts/tj/ladder/la_T1_best12_s${S}_r8.pt ckpts/mcts/
  done
  md5sum ckpts/mcts/*.pt
  echo SETUP_DONE
} > artifacts/mcts/logs/setup_$(hostname).log 2>&1
