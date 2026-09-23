#!/usr/bin/env bash
# Pod setup for run efficiency: Lean 4.34.0 (core) via elan, the fixed Stage-1 lean_seq checkpoint, lean_check self-test.
cd /workspace/nd-takehome; mkdir -p artifacts/ef/logs ckpts/ef
{
  [ -x ~/.elan/bin/lean ] || { curl -sSf https://raw.githubusercontent.com/leanprover/elan/master/elan-init.sh | sh -s -- -y --default-toolchain leanprover/lean4:v4.34.0; }
  ~/.elan/bin/lean --version
  ls -l ckpts/ef/
  nproc; free -g | head -2; nvidia-smi --query-gpu=name,memory.total --format=csv,noheader
  python3 -c "import torch;print('torch',torch.__version__,torch.cuda.is_available())"
  PATH=$HOME/.elan/bin:$PATH python3 lean_check.py --selftest
  echo SETUP_DONE
} > artifacts/ef/logs/setup.log 2>&1
