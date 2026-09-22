#!/usr/bin/env bash
# Pod setup for run lean-only: Lean 4.34.0 (core) via elan, unpack the training set, lean_check self-test. Log: artifacts/lo/logs/setup.log
cd /workspace/nd-takehome; mkdir -p artifacts/lo/logs ckpts/lo ckpts/ladder
{
  [ -x ~/.elan/bin/lean ] || { curl -sSf https://raw.githubusercontent.com/leanprover/elan/master/elan-init.sh | sh -s -- -y --default-toolchain leanprover/lean4:v4.34.0; }
  ~/.elan/bin/lean --version
  [ -f data/train.jsonl ] || gunzip -k data/train.jsonl.gz
  nproc; free -g | head -2; nvidia-smi --query-gpu=name,memory.total --format=csv,noheader
  python3 lean_check.py --selftest
  echo SETUP_DONE
} > artifacts/lo/logs/setup.log 2>&1
