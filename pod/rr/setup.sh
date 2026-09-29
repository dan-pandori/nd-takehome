#!/usr/bin/env bash
# Pod setup for results-registry: Lean 4.34.0 (core), huggingface_hub (the `hf` CLI save_ckpt uploads with), data.
cd /workspace/nd-takehome; mkdir -p artifacts/rr ckpts/rr data/p2 data/ladder
{
  [ -x ~/.elan/bin/lean ] || { curl -sSf https://raw.githubusercontent.com/leanprover/elan/master/elan-init.sh | sh -s -- -y --default-toolchain leanprover/lean4:v4.34.0; }
  ~/.elan/bin/lean --version
  nvidia-smi --query-gpu=name,memory.total --format=csv,noheader
  pip -q install --break-system-packages -U huggingface_hub 2>&1 | tail -1
  B=hf://buckets/dan-pandori/nd-rl/lean-format/data
  hf buckets cp $B/p2/train_depth3_f0_a1.jsonl data/p2/train_depth3_f0_a1.jsonl
  hf buckets cp $B/p2/heldout.jsonl data/p2/heldout.jsonl
  hf buckets cp $B/ladder/rl_targets.jsonl data/ladder/rl_targets.jsonl
  hf buckets cp $B/ladder/transfer.jsonl data/ladder/transfer.jsonl
  head -n 40 data/ladder/rl_targets.jsonl > data/rr_targets40.jsonl
  head -n 40 data/ladder/transfer.jsonl > data/rr_transfer40.jsonl
  head -n 200 data/p2/heldout.jsonl > data/rr_heldout200.jsonl
  wc -l data/p2/*.jsonl data/ladder/*.jsonl data/rr_*.jsonl
  python3 tests/test_registry.py --online
  echo SETUP_DONE
} > artifacts/rr/setup.log 2>&1
