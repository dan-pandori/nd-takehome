#!/usr/bin/env bash
# Pod setup (olmo-answeronly = olmo-transplant's, artifacts under artifacts/olmo_answeronly; both checkpoints are fetched in
# the background from the start, with huggingface_hub pinned to the version the full install resolves to): olmo-think32b's stack (vLLM 0.11.0, transformers 4.57.1 on the template's torch 2.8.0 /
# CUDA 12.8) plus the IF checkers' dependencies at IFBench's uv.lock versions, and their nltk data.
cd /workspace/nd-takehome; A=artifacts/olmo_answeronly; mkdir -p $A/samples $A/graded $A/meta $A/logs /workspace/models
E=$A/meta/pod_env_$(hostname).txt
{ date -u; nvidia-smi --query-gpu=name,memory.total,driver_version,pcie.link.gen.current,pcie.link.width.current --format=csv,noheader
  nvidia-smi topo -m; echo "cpu.max $(cat /sys/fs/cgroup/cpu.max 2>/dev/null) cfs $(cat /sys/fs/cgroup/cpu/cpu.cfs_quota_us 2>/dev/null)"; nproc; free -g | head -2; df -h /workspace / | tail -2; } > $E 2>&1
cat $E
pip install --break-system-packages -q "huggingface_hub[cli,hf_xet]==0.36.2" "hf-xet==1.8.0" 2>&1 | grep -v -i "warning\|notice" | tail -2
bash pod/olmo_ifomega/fetch.sh allenai/Olmo-3-32B-Think-DPO main tok tokenizer.json tokenizer_config.json special_tokens_map.json vocab.json merges.txt config.json generation_config.json
# FETCH (default "dpo s2300"): which checkpoints this pod needs
case " ${FETCH:-dpo s2300} " in *" dpo "*) nohup bash pod/olmo_ifomega/fetch.sh allenai/Olmo-3-32B-Think-DPO main dpo > $A/logs/fetch_dpo.log 2>&1 < /dev/null & ;; esac
case " ${FETCH:-dpo s2300} " in *" s2300 "*) nohup bash pod/olmo_ifomega/fetch.sh allenai/Olmo-3.1-32B-Think main s2300 > $A/logs/fetch_s2300.log 2>&1 < /dev/null & ;; esac
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
pip freeze 2>/dev/null > $A/meta/pip_freeze_$(hostname).txt
echo "SETUP_DONE $(date -u +%FT%TZ)"
