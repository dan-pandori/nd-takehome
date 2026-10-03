#!/usr/bin/env bash
# Pod setup: Lean 4 v4.34.1 core, hf CLI, the cap-6 replay set (state-env p2 train_depth3_f0_a1, 155,000 records), and
# trajectory-cap6's r8 state for seed S at the resume paths.  Usage: bash pod/rc6/setup.sh <seed>
. pod/rc6/env.sh
S=$1; N=la_T1_best6_s$S; D=data/p2/train_depth3_f0_a1.jsonl
{
  [ -x ~/.elan/bin/lean ] || { curl -sSfL https://raw.githubusercontent.com/leanprover/elan/master/elan-init.sh | sh -s -- -y --default-toolchain leanprover/lean4:v4.34.1; }
  ~/.elan/bin/lean --version
  nproc; nvidia-smi --query-gpu=name,memory.total --format=csv,noheader; python3 -c "import torch; print('torch', torch.__version__)"
  pip -q install --break-system-packages -U 'huggingface_hub[cli]' 2>&1 | tail -1
  mkdir -p data/p2 artifacts/rc6/$N
  [ -s $D ] || hf buckets cp $BK/state-env/$D $D
  for f in found_8.jsonl found_transfer_8.jsonl alloc_8.json round_8.json; do
    [ -s artifacts/rc6/$N/$f ] || hf buckets cp $BK/trajectory-cap6/artifacts/tj6/$N/$f artifacts/rc6/$N/$f; done
  [ -s ckpts/rc6/ladder/${N}_r8.pt ] || hf buckets cp $BK/trajectory-cap6/ckpts/tj6/ladder/${N}_r8.pt ckpts/rc6/ladder/${N}_r8.pt
  md5sum $D ckpts/rc6/ladder/${N}_r8.pt artifacts/rc6/$N/*_8.json*; wc -l $D artifacts/rc6/$N/found_8.jsonl artifacts/rc6/$N/found_transfer_8.jsonl
  echo SETUP_DONE
} > artifacts/rc6/logs/setup_s$S.log 2>&1
