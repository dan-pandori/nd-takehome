#!/usr/bin/env bash
# Pod setup for coe-dose01: Lean 4 v4.34.1 core via elan, hf CLI, the arm's pretraining set from create-or-elicit's bucket
# folder (read-only use).  Usage: bash pod/d01/setup.sh <dose01|ko>
. pod/d01/env.sh
ARM=$1; case $ARM in dose01) D=train_k12dose01;; ko) D=train_k12ko;; *) echo "arm?"; exit 1;; esac
{
  [ -x ~/.elan/bin/lean ] || { curl -sSfL https://raw.githubusercontent.com/leanprover/elan/master/elan-init.sh | sh -s -- -y --default-toolchain leanprover/lean4:v4.34.1; }
  ~/.elan/bin/lean --version
  nproc; nvidia-smi --query-gpu=name,memory.total --format=csv,noheader; python3 -c "import torch; print('torch', torch.__version__)"
  python3 -c "import lean_gate; print('lean cpu quota', lean_gate.cpu_quota())"
  pip -q install --break-system-packages -U 'huggingface_hub[cli]' 2>&1 | tail -1
  mkdir -p data/coe
  [ -s data/coe/$D.jsonl ] || { hf buckets cp $BK/create-or-elicit/data/coe/$D.jsonl.gz data/coe/$D.jsonl.gz && gunzip -f data/coe/$D.jsonl.gz; }
  md5sum data/coe/$D.jsonl; wc -l data/coe/$D.jsonl data/coe/*.jsonl data/ladder/rl_targets.jsonl data/p2/heldout.jsonl
  df -h / | tail -1
  echo SETUP_DONE
} > artifacts/coe/logs/setup_$(hostname).log 2>&1
