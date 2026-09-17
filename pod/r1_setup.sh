#!/usr/bin/env bash
# r1-a100 setup: vLLM + model downloads into /workspace/hf. Log: /workspace/nd-takehome/artifacts/r1/setup.log
export HF_HOME=/workspace/hf HF_HUB_ENABLE_HF_TRANSFER=1
mkdir -p /workspace/hf /workspace/nd-takehome/artifacts/r1
cd /workspace/nd-takehome
echo "$(date -u +%T) pip install vllm"
pip install -q --break-system-packages vllm hf_transfer "huggingface_hub[cli]" 2>&1 | tail -3; export PATH=$PATH:/root/.local/bin
python -c "import vllm, torch; print('vllm', vllm.__version__, 'torch', torch.__version__, torch.cuda.is_available())"
echo "$(date -u +%T) download Qwen3-Coder-30B-A3B-Instruct"
hf download Qwen/Qwen3-Coder-30B-A3B-Instruct 2>&1 | tail -1
echo "$(date -u +%T) download Qwen3 small models"
for m in Qwen3-0.6B Qwen3-1.7B Qwen3-4B Qwen3-8B; do hf download Qwen/$m 2>&1 | tail -1; done
echo "$(date -u +%T) SETUP DONE (14B / 32B downloaded later)"
df -h /workspace | tail -1
