#!/usr/bin/env bash
# Pod setup: Lean 4.34.0 (core) via elan + a render self-test of the arm's mode. Log: artifacts/dsr/logs/setup.log
cd /workspace/nd-takehome; mkdir -p artifacts/dsr/logs ckpts/dsr ckpts/ladder
{
  [ -x ~/.elan/bin/lean ] || { curl -sSf https://raw.githubusercontent.com/leanprover/elan/master/elan-init.sh | sh -s -- -y --default-toolchain leanprover/lean4:v4.34.0; }
  ~/.elan/bin/lean --version
  nproc; nvidia-smi --query-gpu=name,memory.total --format=csv,noheader
  python3 -c "import torch;print('torch',torch.__version__,torch.cuda.get_device_name(0))"
  LEAN_GATE_WORKERS=12 python3 dsr_render_check.py --n 500 --lean 300 --neg 100 --modes "$1" --out artifacts/dsr/render_check_pod.json
  echo SETUP_DONE
} > artifacts/dsr/logs/setup.log 2>&1
