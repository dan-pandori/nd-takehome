#!/usr/bin/env bash
# Pod setup (olmo-ifcurve = olmo-ifladder's pod/olmo_ifladder/setup.sh without peft / LoRA checks and without a model
# prefetch): vLLM 0.11.0, transformers 4.57.1 on the template's torch 2.8.0 / CUDA 12.8, the IF checkers' dependencies
# at IFBench's uv.lock versions and their nltk data; the tokenizer files from dpo main (as every stored job used).
cd /workspace/nd-takehome; A=artifacts/olmo_ifcurve; mkdir -p $A/samples $A/graded $A/meta $A/logs $A/queue /workspace/models
E=$A/meta/pod_env_$(hostname).txt
{ date -u; nvidia-smi --query-gpu=name,memory.total,driver_version,pcie.link.gen.current,pcie.link.width.current --format=csv,noheader
  nvidia-smi topo -m; echo "cpu.max $(cat /sys/fs/cgroup/cpu.max 2>/dev/null) cfs $(cat /sys/fs/cgroup/cpu/cpu.cfs_quota_us 2>/dev/null)"; nproc; free -g | head -2; df -h /workspace / | tail -2
  for i in $(seq 0 $(( $(nvidia-smi -L | wc -l) - 1 ))); do echo "GPU $i remapped:"; nvidia-smi -q -i $i | grep -A3 -i "Remapped Rows" | tail -3; done; } > $E 2>&1
cat $E
pip install --break-system-packages -q "huggingface_hub[cli,hf_xet]==0.36.2" "hf-xet==1.8.0" 2>&1 | grep -v -i "warning\|notice" | tail -2
bash pod/olmo_ifomega/fetch.sh allenai/Olmo-3-32B-Think-DPO main tok tokenizer.json tokenizer_config.json special_tokens_map.json vocab.json merges.txt config.json generation_config.json
for x in ${FETCH:-}; do nohup bash pod/olmo_ifomega/fetch.sh allenai/Olmo-3.1-32B-Think $x > $A/logs/fetch_$x.log 2>&1 < /dev/null & done
pip install --break-system-packages -q "vllm==0.11.0" "transformers==4.57.1" "antlr4-python3-runtime==4.11" "huggingface_hub[cli,hf_xet]==0.36.2" "hf-xet==1.8.0" pyarrow pandas \
  "nltk==3.9.2" "langdetect==1.0.9" "emoji==2.15.0" "syllapy==0.8.0" "absl-py==2.3.1" "immutabledict==4.2.2" 2>&1 | grep -v -i "warning\|notice" | tail -5
python -c "import nltk
for p in ['punkt', 'punkt_tab', 'stopwords', 'averaged_perceptron_tagger_eng']: nltk.download(p, quiet=True)
print('NLTK_OK', nltk.__version__)"
python -c "import vllm, torch, transformers, sympy; print('VERSIONS vllm', vllm.__version__, 'torch', torch.__version__, 'transformers', transformers.__version__, 'sympy', sympy.__version__, 'cuda', torch.cuda.is_available(), torch.cuda.device_count())" 2>&1 | tail -1
python -c "
import torch
for i in range(torch.cuda.device_count()):
    x = torch.ones(4096, 4096, device=f'cuda:{i}'); print('CUDA_ALLOC_OK', i, torch.cuda.get_device_name(i), float((x @ x).sum()))
" 2>&1 | tail -8
python -c "import sys; sys.path.insert(0, 'olmo_ifomega'); import grade, json
P = [json.loads(l) for l in open('olmo_ifomega/problems.jsonl')]
print('GRADER_OK', sum(grade.success(p['task'], '<think>x</think>Hello.', p) for p in P[:20]))" 2>&1 | tail -2
NG=$(nvidia-smi -L | wc -l)
# GPU health gate (2026-11-21: a community H200 with 25 uncorrectable remapped rows failed CUDA init): every GPU must pass
# the allocation test above; start.sh starts workers only on GPU_OK and the VPS acquirer replaces a GPU_BAD pod
python -c "
import torch
ok = 0
for i in range(torch.cuda.device_count()):
    try:
        x = torch.randn(8192, 8192, device=f'cuda:{i}'); y = (x @ x).sum().item(); torch.cuda.synchronize(i); ok += 1
    except Exception as e:
        print('GPU_FAIL', i, repr(e)[:120])
print('GPU_TEST', ok, torch.cuda.device_count())
" 2>&1 | tail -3 | tee $A/meta/gpu_test.txt
GT=$(grep GPU_TEST $A/meta/gpu_test.txt | awk '{print $2}')
if [ "$NG" -ge 1 ] && [ "${GT:-0}" = "$NG" ]; then echo "GPU_OK $NG" > $A/meta/gpu_status; else echo "GPU_BAD $NG gpus, ${GT:-0} passed" > $A/meta/gpu_status; fi
cat $A/meta/gpu_status
pip freeze 2>/dev/null > $A/meta/pip_freeze_$(hostname).txt
echo "SETUP_DONE $(date -u +%FT%TZ)"
