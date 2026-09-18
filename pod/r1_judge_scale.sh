#!/usr/bin/env bash
# VPS side: as each scale-ladder model finishes on the pod, pull its outputs and judge them (Lean, batches of 40).
cd /home/dan/work/run1-lean; export PATH=$HOME/.elan/bin:$PATH
for m in Qwen3-0.6B Qwen3-1.7B Qwen3-4B Qwen3-8B Qwen3-14B Qwen3-32B Qwen3-Coder-30B-A3B-Instruct; do
  [ -f artifacts/r1/judged_scale_$m.jsonl ] && { echo "have $m"; continue; }
  until timeout 60 ~/bin/podrun r1-a100 "grep -q 'done $m:' artifacts/r1/gen_scale.log" 2>/dev/null; do sleep 60; done
  timeout 300 ~/runs/run1-lean/pull.sh artifacts/r1/gen_scale_$m.jsonl
  echo "$(date -u +%T) judging $m"
  python3 r1_judge.py --gen artifacts/r1/gen_scale_$m.jsonl --prompts data/r1/scale_prompts.jsonl --out artifacts/r1/judged_scale_$m.jsonl --procs 2 --batch 40 2>&1 | tail -2
done
# the extra: Coder-30B in the token format
until timeout 60 ~/bin/podrun r1-a100 "grep -q 'GEN SCALE2 DONE' artifacts/r1/gen_scale2.log" 2>/dev/null; do sleep 60; done
timeout 300 ~/runs/run1-lean/pull.sh artifacts/r1/gen_scale_tokens_Qwen3-Coder-30B-A3B-Instruct.jsonl
python3 r1_judge.py --gen artifacts/r1/gen_scale_tokens_Qwen3-Coder-30B-A3B-Instruct.jsonl --prompts data/r1/scale_prompts.jsonl --out artifacts/r1/judged_scale_tokens_Qwen3-Coder-30B-A3B-Instruct.jsonl --procs 2 --batch 40 2>&1 | tail -2
for f in gen_scale.log gen_scale2.log; do timeout 120 ~/runs/run1-lean/pull.sh artifacts/r1/$f; done
echo "$(date -u +%T) JUDGE SCALE DONE"
