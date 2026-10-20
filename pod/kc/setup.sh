#!/usr/bin/env bash
# Pod setup for kalmar-complexity: hf CLI, the training sets from the bucket (no Lean needed: nothing is judged here).
. pod/kc/env.sh
{
  nproc; cat /sys/fs/cgroup/cpu.max 2>/dev/null; nvidia-smi --query-gpu=name,memory.total --format=csv,noheader; free -g | head -2; df -h /workspace | tail -1
  python3 -c "import torch; print('torch', torch.__version__, torch.cuda.is_available())"
  pip -q install --break-system-packages -U 'huggingface_hub[cli]' 2>&1 | tail -1
  [ -s data/kalmar/train_kal_sl.jsonl.gz ] || hf buckets cp $BK/kalmar-pretrain/data/kalmar/train_kal_sl.jsonl.gz data/kalmar/train_kal_sl.jsonl.gz
  [ -s data/kh/train_k12.jsonl ] || { hf buckets cp $BK/cap-horizon/data/kh/train_k12.jsonl.gz data/kh/train_k12.jsonl.gz && gunzip -f data/kh/train_k12.jsonl.gz; }
  md5sum data/kalmar/train_kal_sl.jsonl.gz data/kh/train_k12.jsonl data/kalmar/tf1200_kal_sl.jsonl
  echo SETUP_DONE
} > artifacts/kc/logs/setup_$(hostname).log 2>&1
