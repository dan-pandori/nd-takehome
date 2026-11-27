#!/usr/bin/env bash
# Reviewer pod job (olmo-lowrank): environment record, self-test, bucket copies of the run's adapters and of
# olmo-ifladder's LoRAs (sha256 recorded), the seeded checkpoint fetch, then the recompute.
cd /workspace/nd-takehome/rv
export HF_XET_HIGH_PERFORMANCE=1 HF_XET_CHUNK_CACHE_SIZE_BYTES=0 OMP_NUM_THREADS=${NT:-12} MKL_NUM_THREADS=${NT:-12} OPENBLAS_NUM_THREADS=${NT:-12}
pip install --break-system-packages -q "huggingface_hub[hf_xet]==1.32.0" safetensors numpy > pip.log 2>&1
{ date -u; nvidia-smi --query-gpu=name,memory.total --format=csv,noheader; echo "cpu.max $(cat /sys/fs/cgroup/cpu.max 2>/dev/null)"; nproc; free -g | head -2; df -h /root /workspace | tail -2
  python -c "import torch, huggingface_hub, numpy; print('torch', torch.__version__, 'hub', huggingface_hub.__version__, 'numpy', numpy.__version__)"; } > env.txt 2>&1
python rvr_pod.py selftest > selftest.log 2>&1
grep -q 'SELFTEST PASS' selftest.log || { date -u > SELFTEST_FAILED; exit 1; }
( hf buckets sync hf://buckets/dan-pandori/nd-rl/olmo-lowrank/artifacts/olmo_lowrank/adapters /root/rv/adapters > sync_adapters.log 2>&1
  hf buckets sync hf://buckets/dan-pandori/nd-rl/olmo-ifladder/artifacts/olmo_ifladder/lora /root/rv/lora > sync_lora.log 2>&1
  sha256sum /root/rv/adapters/*/adapter_model.safetensors /root/rv/adapters/*/adapter_config.json /root/rv/lora/*/adapter_model.safetensors /root/rv/lora/*/adapter_config.json > adapters_sha.txt
  date -u > SYNC_DONE ) &
python rvr_pod.py fetch plan.json --dl /root/rvdl --ext /root/rvext --inflight 8 > fetch.log 2>&1 || { date -u > FETCH_FAILED; exit 1; }
cp /root/rvext/files.csv files.csv
while [ ! -f SYNC_DONE ]; do sleep 10; done
python rvr_pod.py compute plan.json --ext /root/rvext --out out --lora /root/rv/lora --adapters /root/rv/adapters > compute.log 2>&1
echo "rc $? $(date -u +%FT%TZ)" > JOB_END
