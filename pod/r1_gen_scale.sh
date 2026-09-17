#!/usr/bin/env bash
# Step 3 generation: Qwen3 0.6B..32B (+ Coder-30B as an extra point) on the 208 class theorems, Lean prompt, greedy + 16 samples at T=0.7.
# Waits for the step-2 job to release the GPU.
export HF_HOME=/workspace/hf PATH=$PATH:/root/.local/bin
cd /workspace/nd-takehome
until grep -q "GEN CODER DONE" artifacts/r1/gen_coder30b.log 2>/dev/null; do sleep 60; done
for m in Qwen3-0.6B Qwen3-1.7B Qwen3-4B Qwen3-8B Qwen3-14B Qwen3-32B Qwen3-Coder-30B-A3B-Instruct; do
  hf download Qwen/$m 2>&1 | tail -1
  echo "$(date -u +%T) start $m"
  python r1_gen.py --model Qwen/$m --prompts data/r1/scale_prompts.jsonl --forms lean --draws 0 --n 16 --temperature 0.7 --greedy \
    --max_tokens 2048 --max_model_len 12288 --gpu_mem 0.92 --out artifacts/r1/gen_scale_$m.jsonl > artifacts/r1/gen_scale_$m.log 2>&1
  echo "$(date -u +%T) done $m: $(grep -c . artifacts/r1/gen_scale_$m.jsonl) records"
done
echo "$(date -u +%T) GEN SCALE DONE"
