#!/usr/bin/env bash
# Step 2 generation: Qwen3-Coder-30B-A3B-Instruct, 3 forms x 5 draws x 236 theorems, greedy + 8 samples at T=0.7.
export HF_HOME=/workspace/hf PATH=$PATH:/root/.local/bin
cd /workspace/nd-takehome
python r1_gen.py --model Qwen/Qwen3-Coder-30B-A3B-Instruct --prompts data/r1/prompts.jsonl --forms tokens,lean,english \
  --draws 0,1,2,3,4 --n 8 --temperature 0.7 --greedy --max_tokens 2048 --max_model_len 12288 --out artifacts/r1/gen_coder30b.jsonl
echo "$(date -u +%T) GEN CODER DONE"
