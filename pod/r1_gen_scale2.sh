#!/usr/bin/env bash
# Extra after the scale ladder: Coder-30B on the class theorems in the TOKEN format (the task RL solved), greedy + 16 samples.
export HF_HOME=/workspace/hf PATH=$PATH:/root/.local/bin
cd /workspace/nd-takehome
until grep -q "GEN SCALE DONE" artifacts/r1/gen_scale.log 2>/dev/null; do sleep 60; done
echo "$(date -u +%T) start coder tokens"
python r1_gen.py --model Qwen/Qwen3-Coder-30B-A3B-Instruct --prompts data/r1/scale_prompts.jsonl --forms tokens --draws 0 --n 16 --temperature 0.7 --greedy \
  --max_tokens 2048 --max_model_len 12288 --gpu_mem 0.92 --out artifacts/r1/gen_scale_tokens_Qwen3-Coder-30B-A3B-Instruct.jsonl > artifacts/r1/gen_scale_tokens_coder.log 2>&1
echo "$(date -u +%T) GEN SCALE2 DONE: $(grep -c . artifacts/r1/gen_scale_tokens_Qwen3-Coder-30B-A3B-Instruct.jsonl) records"
