#!/usr/bin/env bash
# Pod setup for J8: hf CLI and the start checkpoints (trajectory's step 1,600 / 5,000 / 12,000 / 16,000) for seeds 0-2.
. pod/cd/env.sh
{
  pip -q install --break-system-packages -U 'huggingface_hub[cli]' 2>&1 | tail -1
  for s in 0 1 2; do for st in 1600 5000 12000 16000; do
    [ -s $CK/s${s}_p${st}.pt ] || hf buckets cp $BK/trajectory/ckpts/tj/stage1_best12_s${s}_b1200_step${st}.pt $CK/s${s}_p${st}.pt
  done; done
  md5sum $CK/*.pt; echo SETUP_DONE
} > artifacts/cd/logs/setup_h_$(hostname).log 2>&1
