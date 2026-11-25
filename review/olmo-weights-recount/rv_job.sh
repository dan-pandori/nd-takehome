#!/usr/bin/env bash
# Reviewer pod job (olmo-weights): environment record, self-test (cuda + cpu), then the seeded recompute.
cd /workspace/nd-takehome/rv
export HF_XET_HIGH_PERFORMANCE=1 HF_XET_CHUNK_CACHE_SIZE_BYTES=0
pip install --break-system-packages -q "huggingface_hub[hf_xet]==0.36.2" "hf-xet==1.8.0" safetensors numpy > pip.log 2>&1
{ date -u; nvidia-smi --query-gpu=name,memory.total --format=csv,noheader; echo "cpu.max $(cat /sys/fs/cgroup/cpu.max)"; nproc; free -g | head -2; df -h /root /workspace | tail -2
  python -c "import torch, huggingface_hub, numpy; print('torch', torch.__version__, 'hub', huggingface_hub.__version__, 'numpy', numpy.__version__)"; } > env.txt 2>&1
python rv_selftest.py cuda > selftest.log 2>&1; python rv_selftest.py cpu >> selftest.log 2>&1
[ "$(grep -c 'SELFTEST PASS' selftest.log)" = 2 ] || { date -u > SELFTEST_FAILED; exit 1; }
python rv_recompute.py plan.json out --dl /root/rvdl --cap-gb ${CAP:-450} --inflight 8 --lora-dir /workspace/nd-takehome/rv/lora > run.log 2>&1
echo "rc $? $(date -u +%FT%TZ)" > JOB_END
