#!/usr/bin/env bash
# Pod setup for capability-defs: Lean 4 core via elan, hf CLI, cap-12 best-cap12 checkpoints init / pend / r8 / r16 for
# seeds 0-2 from the bucket (md5 logged; expected md5s in capability_defs/analysis/INVENTORY.md § C).
. pod/cd/env.sh
{
  [ -x ~/.elan/bin/lean ] || { curl -sSfL https://raw.githubusercontent.com/leanprover/elan/master/elan-init.sh | sh -s -- -y --default-toolchain leanprover/lean4:v4.34.1; }
  ~/.elan/bin/lean --version
  nproc; free -g | head -2; nvidia-smi --query-gpu=name,memory.total --format=csv,noheader; python3 -c "import torch; print('torch', torch.__version__)"
  pip -q install --break-system-packages -U 'huggingface_hub[cli]' 2>&1 | tail -1
  for s in 0 1 2; do
    [ -s $CK/s${s}_init.pt ] || hf buckets cp $BK/trajectory/ckpts/tj/stage1_best12_s${s}_b1200_step0.pt $CK/s${s}_init.pt
    [ -s $CK/s${s}_pend.pt ] || hf buckets cp $BK/trajectory/ckpts/tj/stage1_best12_s${s}_b1200.pt $CK/s${s}_pend.pt
    [ -s $CK/s${s}_r8.pt ] || hf buckets cp $BK/trajectory/ckpts/tj/ladder/la_T1_best12_s${s}_r8.pt $CK/s${s}_r8.pt
    [ -s $CK/s${s}_r16.pt ] || hf buckets cp $BK/rl-continue/ckpts/rc/ladder/la_T1_best12_s${s}_r16.pt $CK/s${s}_r16.pt
  done
  md5sum $CK/*.pt; ls -la $CK
  echo SETUP_DONE
} > artifacts/cd/logs/setup_$(hostname).log 2>&1
