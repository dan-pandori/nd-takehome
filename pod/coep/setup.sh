#!/usr/bin/env bash
# Pod setup: Lean 4 v4.34.1 core via elan, hf CLI, the checkpoints C1-C3 read (pre-registration create-or-elicit-paper).
. pod/coep/env.sh
{
  [ -x ~/.elan/bin/lean ] || { curl -sSfL https://raw.githubusercontent.com/leanprover/elan/master/elan-init.sh | sh -s -- -y --default-toolchain leanprover/lean4:v4.34.1; }
  ~/.elan/bin/lean --version
  nproc; nvidia-smi --query-gpu=name,memory.total --format=csv,noheader; python3 -c "import torch; print('torch', torch.__version__)"
  python3 -c "import lean_gate; print('lean cpu quota', lean_gate.cpu_quota())"
  pip -q install --break-system-packages -U 'huggingface_hub[cli]' 2>&1 | tail -n 1
  for c in la_ko_s0_r16 la_ko_s1_r16 la_ko_s2_r16 la_ko_s3_r16 la_ko_s4_r16 la_ko_s5_r16 la_dose1_s0_r16 la_dose1_s1_r16 la_dose1_s2_r16 la_full_s4_r16; do
    [ -s ckpts/coe_paper/$c.pt ] || hf buckets cp $BK/create-or-elicit/ckpts/coe/ladder/$c.pt ckpts/coe_paper/$c.pt
  done
  for S in 0 1 2; do
    [ -s ckpts/coe_paper/stage1_best12_s${S}_b1200.pt ] || hf buckets cp $BK/trajectory/ckpts/tj/stage1_best12_s${S}_b1200.pt ckpts/coe_paper/stage1_best12_s${S}_b1200.pt
  done
  ls -la ckpts/coe_paper; md5sum ckpts/coe_paper/*.pt
  wc -l data/coe_paper/*.jsonl
  echo SETUP_DONE
} > artifacts/coe_paper/logs/setup_$(hostname).log 2>&1
