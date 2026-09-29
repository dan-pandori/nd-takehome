#!/usr/bin/env bash
# long-pool-2 pod setup: Lean 4.34.0 core via elan, hf CLI, the 12 re-read checkpoints from the bucket (+ sha256 prefixes).
cd /workspace/nd-takehome; mkdir -p ckpts/sc12/ladder ckpts/ladder ckpts/se artifacts/lpool2
{
  [ -x ~/.elan/bin/lean ] || { curl -sSf https://raw.githubusercontent.com/leanprover/elan/master/elan-init.sh | sh -s -- -y --default-toolchain leanprover/lean4:v4.34.0; }
  ~/.elan/bin/lean --version
  pip -q install --break-system-packages -U 'huggingface_hub[cli]' 2>&1 | tail -1
  B=hf://buckets/dan-pandori/nd-rl
  for s in 0 1 2 3; do hf buckets cp $B/state-cap12/ckpts/sc12/ladder/la_T1_SN12_s${s}_r8.pt ckpts/sc12/ladder/la_T1_SN12_s${s}_r8.pt
                       hf buckets cp $B/state-cap12/ckpts/sc12/stage1_SN12_s$s.pt ckpts/sc12/stage1_SN12_s$s.pt; done
  for s in 0 1; do hf buckets cp $B/state-cap12/ckpts/ladder/la_T1_K12_s${s}_r8.pt ckpts/ladder/la_T1_K12_s${s}_r8.pt
                   hf buckets cp $B/state-env/ckpts/se/ladder/la_T1_SN_s${s}_r8.pt ckpts/se/la_T1_SN_s${s}_r8.pt; done
  sha256sum ckpts/sc12/*.pt ckpts/sc12/ladder/*.pt ckpts/ladder/*.pt ckpts/se/*.pt | awk '{print substr($1,1,16), $2}' > artifacts/lpool2/ckpt_sha.txt
  cat artifacts/lpool2/ckpt_sha.txt; echo SETUP_DONE
} > artifacts/lpool2/setup.log 2>&1
grep -q SETUP_DONE artifacts/lpool2/setup.log && [ $(wc -l < artifacts/lpool2/ckpt_sha.txt) = 12 ]
