#!/usr/bin/env bash
# A: seed-1 column. base s1 + EI s1rerun, 383 theorems, T 0.8, k 10,000, stop 50 (= support-curves stage 3).
# Two jobs per 32 GB card at batch 4096 (four OOM'd: ~10.5 GB each + KV growth).
cd /workspace/nd-takehome; export PATH=$HOME/.elan/bin:$PATH LEAN_GATE_WORKERS=${LGW:-8}
B=${BATCH:-4096}
python3 support.py --ckpt ckpts/lf/stage1_a1_seq_s1.pt --model base --stage a --k 10000 --stop_at 50 --temperature 0.8 \
  --seed 101 --model_seed 1 --batch $B --max_new 512 --shard 0/1 --out artifacts/sf/a_base_T08_s1 > artifacts/sf/logs/a_base.log 2>&1 &
python3 support.py --ckpt ckpts/ladder/la_T1_sc_s1rerun_r8.pt --model ei --stage a --k 10000 --stop_at 50 --temperature 0.8 \
  --seed 101 --model_seed 1 --batch $B --max_new 512 --shard 0/1 --out artifacts/sf/a_ei_T08_s1rerun > artifacts/sf/logs/a_ei.log 2>&1 &
wait; echo A_DONE
