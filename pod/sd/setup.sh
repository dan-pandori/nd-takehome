#!/usr/bin/env bash
# Pod setup: Lean 4.34.0 (core) via elan (sd_eval.py's judge), the hf CLI (so trajectory checkpoints
# upload from the pod), a self-test of the Lean checker, and the machine's real CPU quota.
# Log: artifacts/sd/logs/setup.log
cd /workspace/nd-takehome; mkdir -p artifacts/sd/logs artifacts/sd/ev ckpts/sd
{
  [ -x ~/.elan/bin/lean ] || { curl -sSf https://raw.githubusercontent.com/leanprover/elan/master/elan-init.sh | sh -s -- -y --default-toolchain leanprover/lean4:v4.34.0; }
  ~/.elan/bin/lean --version
  nproc; cat /sys/fs/cgroup/cpu.max 2>/dev/null; free -g | head -2
  nvidia-smi --query-gpu=name,memory.total --format=csv,noheader
  python3 -c "import torch; print('torch', torch.__version__, torch.cuda.get_device_name(0))"
  pip install -q -U 'huggingface_hub[cli]' 2>&1 | tail -2; python3 -m huggingface_hub.commands.huggingface_cli version 2>/dev/null || hf version
  PATH=$HOME/.elan/bin:$PATH LEAN_GATE_WORKERS=6 LEAN_GATE_LOG=artifacts/sd/gate_selftest.jsonl python3 pod/lf/gate_selftest.py
  echo SETUP_DONE
} > artifacts/sd/logs/setup.log 2>&1
