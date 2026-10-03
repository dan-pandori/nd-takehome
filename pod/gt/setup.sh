#!/usr/bin/env bash
# Pod setup for guided-tts: Lean 4 core via elan, hf CLI, the six r8 checkpoints from the bucket (md5 logged).
. pod/gt/env.sh
{
  [ -x ~/.elan/bin/lean ] || { curl -sSfL https://raw.githubusercontent.com/leanprover/elan/master/elan-init.sh | sh -s -- -y --default-toolchain leanprover/lean4:v4.34.1; }
  ~/.elan/bin/lean --version
  nproc; nvidia-smi --query-gpu=name,memory.total --format=csv,noheader; python3 -c "import torch; print('torch', torch.__version__)"
  pip -q install --break-system-packages -U 'huggingface_hub[cli]' 2>&1 | tail -1
  for s in 0 1 2; do
    [ -s ckpts/gt/la_T1_best12_s${s}_r8.pt ] || hf buckets cp $BK/trajectory/ckpts/tj/ladder/la_T1_best12_s${s}_r8.pt ckpts/gt/la_T1_best12_s${s}_r8.pt
    [ -s ckpts/gt/la_T1_best6_s${s}_r8.pt ] || hf buckets cp $BK/trajectory-cap6/ckpts/tj6/ladder/la_T1_best6_s${s}_r8.pt ckpts/gt/la_T1_best6_s${s}_r8.pt
  done
  md5sum ckpts/gt/*.pt; ls -la ckpts/gt
  echo SETUP_DONE
} > artifacts/gt/logs/setup_$(hostname).log 2>&1
