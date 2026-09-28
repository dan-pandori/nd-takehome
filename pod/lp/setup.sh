#!/usr/bin/env bash
# lean-prefilter pod setup: Lean 4.34.0 core, the checkpoints and train set from the bucket, selftests.
cd /workspace/nd-takehome; mkdir -p artifacts/lp ckpts/lp data/dsc
{
  [ -x ~/.elan/bin/lean ] || { curl -sSf https://raw.githubusercontent.com/leanprover/elan/master/elan-init.sh | sh -s -- -y --default-toolchain leanprover/lean4:v4.34.0; }
  ~/.elan/bin/lean --version; nproc; cat /sys/fs/cgroup/cpu.max 2>/dev/null || echo "no cpu.max"
  nvidia-smi --query-gpu=name,memory.total --format=csv,noheader
  python3 -c "import torch; print('cuda', torch.cuda.is_available())"
  B=hf://buckets/dan-pandori/nd-rl
  for f in ds-composition/ckpts/dsc/stage1_a1_s1.pt ds-composition/ckpts/dsc/stage1_a3_s0.pt ds-generator/ckpts/dsg/stage1_g2_s0.pt \
           lean-format/ckpts/lf/stage1_a1_rand_s0.pt lean-format/ckpts/lf/stage1_full_seq.pt lean-format/ckpts/lf/ei_d3_seq_s0_r8.pt \
           cap-horizon/ckpts/kh/stage1_k14_s0.pt noise-floor/ckpts/nf/stage1_p2_s3.pt; do
    o=ckpts/lp/$(echo $f | cut -d/ -f1)__$(basename $f); [ -s $o ] || hf buckets cp $B/$f $o > /dev/null
  done
  [ -s data/dsc/train_a1.jsonl ] || { hf buckets cp $B/ds-composition/data/dsc/train_a1.jsonl.gz data/dsc/train_a1.jsonl.gz > /dev/null && gunzip -f data/dsc/train_a1.jsonl.gz; }
  mkdir -p ckpts/dsc; ln -sf ../lp/ds-composition__stage1_a1_s1.pt ckpts/dsc/stage1_a1_s1.pt
  ls -la ckpts/lp data/dsc; wc -l data/dsc/train_a1.jsonl
  python3 -c "import lean_gate; print('workers', lean_gate.WORKERS, 'prefilter', lean_gate.PREFILTER, 'pipeline', lean_gate.PIPELINE)"
  PATH=$HOME/.elan/bin:$PATH LEAN_GATE_LOG=/tmp/tg.jsonl python3 tests/test_lean_only_judge.py 2>&1 | tail -2
  PATH=$HOME/.elan/bin:$PATH python3 tests/test_lean_prefilter.py 2>&1 | tail -2
} 2>&1 | tee artifacts/lp/setup.log
