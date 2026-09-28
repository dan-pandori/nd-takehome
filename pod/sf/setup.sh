#!/usr/bin/env bash
# Pod setup for run state-frontier: Lean 4.34.0 via elan, hf CLI, the state-env data, the L_true >= 11 pool.
cd /workspace/nd-takehome; mkdir -p artifacts/sf2 ckpts/sf2 data/p2 data/ladder data/sf2
{
  [ -x ~/.elan/bin/lean ] || { curl -sSf https://raw.githubusercontent.com/leanprover/elan/master/elan-init.sh | sh -s -- -y --default-toolchain leanprover/lean4:v4.34.0; }
  ~/.elan/bin/lean --version
  nproc; nvidia-smi --query-gpu=name,memory.total --format=csv,noheader
  pip -q install --break-system-packages -U 'huggingface_hub[cli]' 2>&1 | tail -1
  B=hf://buckets/dan-pandori/nd-rl/state-env/data
  for f in p2/train_depth3_f0_a1.jsonl p2/heldout.jsonl ladder/rl_targets.jsonl ladder/transfer.jsonl; do hf buckets cp $B/$f data/$f; done
  python3 -c "
import json
rs=[json.loads(l) for l in open('data/ladder/transfer.jsonl')]
with open('data/sf2/long.jsonl','w') as f:
    for r in rs:
        if r['L_true']>=11: f.write(json.dumps(r)+'\n')"
  wc -l data/p2/*.jsonl data/ladder/*.jsonl data/sf2/long.jsonl; md5sum data/sf2/long.jsonl
  echo SETUP_DONE
} > artifacts/sf2/setup.log 2>&1
