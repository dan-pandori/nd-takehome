#!/usr/bin/env bash
# A, base arm: runs after the EI arm finishes (two batch-4096 / max_new-512 jobs do not fit in 32 GB).
cd /workspace/nd-takehome; export PATH=$HOME/.elan/bin:$PATH LEAN_GATE_WORKERS=8
while pgrep -f "[l]a_T1_sc_s1rerun_r8" >/dev/null; do sleep 30; done
rm -f artifacts/sf/a_base_T08_s1.s0.jsonl
python3 support.py --ckpt ckpts/lf/stage1_a1_seq_s1.pt --model base --stage a --k 10000 --stop_at 50 --temperature 0.8 \
  --seed 101 --model_seed 1 --batch 4096 --max_new 512 --shard 0/1 --out artifacts/sf/a_base_T08_s1 > artifacts/sf/logs/a_base.log 2>&1
echo A_BASE_DONE
