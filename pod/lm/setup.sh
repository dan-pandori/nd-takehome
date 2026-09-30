#!/usr/bin/env bash
# lit-measures pod setup: hf CLI, the noise-floor p1 training set, the held-out set; an origin/dan copy of the trainer
# in /workspace/orig for the default-reproduction check (pushed by pod/lm/push_orig.sh).
cd /workspace/nd-takehome; mkdir -p artifacts/lit-measures/m2 data/nf data/p2
{
  nproc; nvidia-smi --query-gpu=name,memory.total --format=csv,noheader
  pip -q install --break-system-packages -U 'huggingface_hub[cli]' 2>&1 | tail -1
  B=hf://buckets/dan-pandori/nd-rl
  hf buckets cp $B/noise-floor/data/nf/train_p1.jsonl data/nf/train_p1.jsonl
  hf buckets cp $B/lean-format/data/p2/heldout.jsonl data/p2/heldout.jsonl
  md5sum data/nf/train_p1.jsonl data/p2/heldout.jsonl; wc -l data/nf/train_p1.jsonl data/p2/heldout.jsonl
  echo SETUP_DONE
} > artifacts/lit-measures/m2/setup_$(hostname).log 2>&1
