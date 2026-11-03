#!/usr/bin/env bash
# Pod setup: vLLM 0.11.0 (the version open-instruct pinned for RL) on the template's torch 2.8.0 / CUDA 12.8.
cd /workspace/nd-takehome; A=artifacts/olmo_pilot; mkdir -p $A/samples $A/graded $A/meta $A/logs $A/ll /workspace/models
{ date -u; nvidia-smi --query-gpu=name,memory.total,driver_version --format=csv,noheader; echo "cpu.max $(cat /sys/fs/cgroup/cpu.max 2>/dev/null) cfs $(cat /sys/fs/cgroup/cpu/cpu.cfs_quota_us 2>/dev/null)"; nproc; free -g | head -2; df -h /workspace / | tail -2; } > $A/meta/pod_env_$(hostname).txt 2>&1
cat $A/meta/pod_env_$(hostname).txt
pip install --break-system-packages -q "vllm==0.11.0" "transformers==4.57.1" "antlr4-python3-runtime==4.11" "huggingface_hub[cli,hf_xet]" 2>&1 | grep -v -i "warning\|notice" | tail -5
python -c "import vllm, torch, transformers, sympy; print('VERSIONS vllm', vllm.__version__, 'torch', torch.__version__, 'transformers', transformers.__version__, 'sympy', sympy.__version__, 'cuda', torch.cuda.is_available())" 2>&1 | tail -1
python -c "import torch; x = torch.ones(1024, 1024, device='cuda'); print('CUDA_ALLOC_OK', float((x @ x).sum()))" 2>&1 | tail -1
pip freeze 2>/dev/null > $A/meta/pip_freeze_$(hostname).txt
bash pod/olmo_pilot/fetch.sh allenai/Olmo-3-1025-7B main base_tok tokenizer.json tokenizer_config.json special_tokens_map.json vocab.json merges.txt config.json
echo "SETUP_DONE $(date -u +%FT%TZ)"
