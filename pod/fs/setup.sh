#!/usr/bin/env bash
# Pod setup: Lean 4.34.0 (sd_eval.py's judge), versions, CPU quota, Lean self-test. Log: artifacts/fs/logs/setup.log
cd /workspace/nd-takehome; mkdir -p artifacts/fs/logs artifacts/fs/ev ckpts/fs
{
  [ -x ~/.elan/bin/lean ] || { curl -sSf https://raw.githubusercontent.com/leanprover/elan/master/elan-init.sh | sh -s -- -y --default-toolchain leanprover/lean4:v4.34.0; }
  ~/.elan/bin/lean --version
  nproc; cat /sys/fs/cgroup/cpu.max 2>/dev/null; free -g | head -2
  nvidia-smi --query-gpu=name,memory.total,clocks.max.sm --format=csv,noheader
  python3 -c "import torch, triton; print('torch', torch.__version__, 'triton', triton.__version__, torch.cuda.get_device_name(0))"
  PATH=$HOME/.elan/bin:$PATH LEAN_GATE_WORKERS=6 LEAN_GATE_LOG=artifacts/fs/gate_selftest.jsonl python3 pod/lf/gate_selftest.py
  echo SETUP_DONE
} > artifacts/fs/logs/setup.log 2>&1
