#!/usr/bin/env bash
# Pod setup: Lean 4.34.0 (core) via elan, gunzip the arm's training set, self-test of the Lean gate. Log: artifacts/kh/logs/setup.log
cd /workspace/nd-takehome; mkdir -p artifacts/kh/logs ckpts/kh ckpts/ladder
{
  [ -x ~/.elan/bin/lean ] || { curl -sSf https://raw.githubusercontent.com/leanprover/elan/master/elan-init.sh | sh -s -- -y --default-toolchain leanprover/lean4:v4.34.0; }
  ~/.elan/bin/lean --version
  for f in data/kh/*.jsonl.gz data/p2/*.jsonl.gz; do [ -e "$f" ] || continue; [ -f "${f%.gz}" ] || gunzip -k "$f"; done
  nproc; nvidia-smi --query-gpu=name,memory.total --format=csv,noheader; python3 -c "import torch; print(torch.__version__, torch.cuda.is_available())"
  export PATH=$HOME/.elan/bin:$PATH; LEAN_GATE_LOG=artifacts/kh/gate_selftest.jsonl python3 pod/kh/gate_selftest.py
  echo SETUP_DONE
} > artifacts/kh/logs/setup.log 2>&1
