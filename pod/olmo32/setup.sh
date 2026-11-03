#!/usr/bin/env bash
# Pod setup (olmo-think32b): vLLM 0.11.0 (open-instruct's RL pin; the pilot's) on the template's torch 2.8.0 / CUDA 12.8.
cd /workspace/nd-takehome; A=artifacts/olmo32; mkdir -p $A/samples $A/graded $A/meta $A/logs /workspace/models
E=$A/meta/pod_env_$(hostname).txt
{ date -u; nvidia-smi --query-gpu=name,memory.total,driver_version,pcie.link.gen.current,pcie.link.width.current --format=csv,noheader
  nvidia-smi topo -m; echo "cpu.max $(cat /sys/fs/cgroup/cpu.max 2>/dev/null)"; nproc; free -g | head -2; df -h /workspace / | tail -2; } > $E 2>&1
cat $E
pip install --break-system-packages -q "vllm==0.11.0" "transformers==4.57.1" "antlr4-python3-runtime==4.11" "huggingface_hub[cli,hf_xet]" pyarrow pandas 2>&1 | grep -v -i "warning\|notice" | tail -5
python -c "import vllm, torch, transformers, sympy; print('VERSIONS vllm', vllm.__version__, 'torch', torch.__version__, 'transformers', transformers.__version__, 'sympy', sympy.__version__, 'cuda', torch.cuda.is_available(), torch.cuda.device_count())" 2>&1 | tail -1
python -c "
import torch
for i in range(torch.cuda.device_count()):
    x = torch.ones(4096, 4096, device=f'cuda:{i}'); print('CUDA_ALLOC_OK', i, torch.cuda.get_device_name(i), float((x @ x).sum()))
" 2>&1 | tail -8
pip freeze 2>/dev/null > $A/meta/pip_freeze_$(hostname).txt
bash pod/olmo32/fetch.sh allenai/Olmo-3-32B-Think-DPO main tok tokenizer.json tokenizer_config.json special_tokens_map.json vocab.json merges.txt config.json generation_config.json
echo "SETUP_DONE $(date -u +%FT%TZ)"
