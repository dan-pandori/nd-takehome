#!/usr/bin/env bash
# Pod setup for style-edl: Lean 4 v4.34.1 core via elan, hf CLI, the six checkpoints from the best-state bucket.
. pod/sedl/env.sh
{
  [ -x ~/.elan/bin/lean ] || { curl -sSfL https://raw.githubusercontent.com/leanprover/elan/master/elan-init.sh | sh -s -- -y --default-toolchain leanprover/lean4:v4.34.1; }
  ~/.elan/bin/lean --version
  nproc; cat /sys/fs/cgroup/cpu.max 2>/dev/null; nvidia-smi --query-gpu=name,memory.total --format=csv,noheader; free -g | head -2; df -h /workspace | tail -1
  python3 -c "import torch; print('torch', torch.__version__, torch.cuda.is_available())"
  pip -q install --break-system-packages -U 'huggingface_hub[cli]' 2>&1 | tail -1
  python3 -c "import lean_gate; print('lean cpu quota', lean_gate.cpu_quota())"
  for s in 0 1 2; do
    [ -s ckpts/bs/stage1_best12_s${s}_b1200.pt ] || hf buckets cp $BK/best-state/ckpts/bs/stage1_best12_s${s}_b1200.pt ckpts/bs/stage1_best12_s${s}_b1200.pt
    [ -s ckpts/bs/ladder/la_T1_best12_s${s}_r8.pt ] || hf buckets cp $BK/best-state/ckpts/bs/ladder/la_T1_best12_s${s}_r8.pt ckpts/bs/ladder/la_T1_best12_s${s}_r8.pt
  done
  md5sum ckpts/bs/*.pt ckpts/bs/ladder/*.pt data/kalmar/tf1200_kal_sl.jsonl
  echo SETUP_DONE
} > artifacts/style_edl/logs/setup_$(hostname).log 2>&1
