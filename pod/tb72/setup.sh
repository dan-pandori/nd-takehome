#!/usr/bin/env bash
# Pod setup for textbook72: Lean 4 v4.34.1 core via elan, hf CLI, the 12 checkpoints from the bucket.
. pod/tb72/env.sh
{
  [ -x ~/.elan/bin/lean ] || { curl -sSfL https://raw.githubusercontent.com/leanprover/elan/master/elan-init.sh | sh -s -- -y --default-toolchain leanprover/lean4:v4.34.1; }
  ~/.elan/bin/lean --version
  nproc; cat /sys/fs/cgroup/cpu.max 2>/dev/null; echo LEAN_GATE_WORKERS=$LEAN_GATE_WORKERS
  nvidia-smi --query-gpu=name,memory.total --format=csv,noheader
  pip -q install --break-system-packages -U 'huggingface_hub[cli]' 2>&1 | tail -1
  for s in 0 1 2 3; do
    hf buckets cp $BK/state-cap12/ckpts/sc12/ladder/la_T1_SN12_s${s}_r8.pt ckpts/tb72/T1_SN12_s$s.pt
    hf buckets cp $BK/state-cap12/ckpts/sc12/stage1_SN12_s$s.pt ckpts/tb72/Fz_SN12_s$s.pt
  done
  for s in 0 1; do
    hf buckets cp $BK/state-env/ckpts/se/ladder/la_T1_SN_s${s}_r8.pt ckpts/tb72/T1_SN6_s$s.pt
    hf buckets cp $BK/state-env/ckpts/se/stage1_SN_s$s.pt ckpts/tb72/Fz_SN6_s$s.pt
  done
  ls -la ckpts/tb72; md5sum ckpts/tb72/*.pt
  cat data/eval_only/textbook72/textbook_dev.jsonl data/eval_only/textbook72/textbook_train.jsonl > data/tb72/all72.jsonl
  sha256sum data/eval_only/textbook72/*.jsonl; wc -l data/tb72/all72.jsonl
  echo SETUP_DONE
} > artifacts/textbook72/logs/setup.log 2>&1
