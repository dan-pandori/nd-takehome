#!/usr/bin/env bash
# Pod setup for olmo-weights: record the pod (GPU, CPU quota, RAM, disk), install the downloader and safetensors on the
# template's torch, run the engine self-test on CPU and GPU.
cd /workspace/nd-takehome; A=artifacts/olmo_weights; mkdir -p $A/logs $A/stats $A/stage0
E=$A/logs/pod_env_$(hostname).txt
{ date -u; nvidia-smi --query-gpu=name,memory.total,driver_version --format=csv,noheader 2>&1
  echo "cpu.max $(cat /sys/fs/cgroup/cpu.max 2>/dev/null)"; echo "nproc $(nproc)"; free -g | head -2; df -h /workspace / | tail -2
  cat /proc/cpuinfo | grep -m1 "model name"; } > $E 2>&1
pip install --break-system-packages -q "huggingface_hub[hf_xet]==0.36.2" "hf-xet==1.8.0" hf_transfer safetensors numpy 2>&1 | grep -v -i "warning\|notice" | tail -3
python -c "import huggingface_hub, safetensors, torch, numpy; print('VERSIONS hub', huggingface_hub.__version__, 'safetensors', safetensors.__version__, 'torch', torch.__version__, 'cuda', torch.cuda.is_available(), 'numpy', numpy.__version__)" >> $E 2>&1
pip show hf-xet 2>/dev/null | grep -i '^version' | sed 's/^/hf-xet /' >> $E
cat $E
python olmo_weights/selftest.py --device cpu --dir /tmp/ow_st_cpu 2>&1 | tail -6
python olmo_weights/selftest.py --device cuda --dir /tmp/ow_st_cuda 2>&1 | tail -6
python olmo_weights/selftest.py --device cuda --dir /tmp/ow_st_cuda_tiny --cache-gb 4e-6 2>&1 | tail -6
echo SETUP_DONE
