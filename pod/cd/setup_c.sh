#!/usr/bin/env bash
# Pod setup for capability-defs pod C: Lean, hf CLI, cap-6 best-cap6 pend / r8 / r16 and cap-12 r16 checkpoints.
. pod/cd/env.sh
{
  [ -x ~/.elan/bin/lean ] || { curl -sSfL https://raw.githubusercontent.com/leanprover/elan/master/elan-init.sh | sh -s -- -y --default-toolchain leanprover/lean4:v4.34.1; }
  ~/.elan/bin/lean --version
  nproc; free -g | head -2; nvidia-smi --query-gpu=name,memory.total --format=csv,noheader; python3 -c "import torch; print('torch', torch.__version__)"
  pip -q install --break-system-packages -U 'huggingface_hub[cli]' 2>&1 | tail -1
  for s in 0 1 2; do
    [ -s $CK/c6_s${s}_pend.pt ] || hf buckets cp $BK/trajectory-cap6/ckpts/tj6/stage1_best6_s${s}_b1200.pt $CK/c6_s${s}_pend.pt
    [ -s $CK/c6_s${s}_r8.pt ] || hf buckets cp $BK/trajectory-cap6/ckpts/tj6/ladder/la_T1_best6_s${s}_r8.pt $CK/c6_s${s}_r8.pt
    [ -s $CK/c6_s${s}_r16.pt ] || hf buckets cp $BK/rl-continue-cap6/ckpts/rc6/ladder/la_T1_best6_s${s}_r16.pt $CK/c6_s${s}_r16.pt
    [ -s $CK/s${s}_r16.pt ] || hf buckets cp $BK/rl-continue/ckpts/rc/ladder/la_T1_best12_s${s}_r16.pt $CK/s${s}_r16.pt
  done
  md5sum $CK/*.pt; ls -la $CK
  echo SETUP_DONE
} > artifacts/cd/logs/setup_c_$(hostname).log 2>&1
