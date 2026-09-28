#!/usr/bin/env bash
# B: 6 longest survivors (L_true 11/12), base s0, T 1.0, up to 1,666,667 more attempts each, stop at 5. One job per theorem.
cd /workspace/nd-takehome; export PATH=$HOME/.elan/bin:$PATH LEAN_GATE_WORKERS=${LGW:-8}
B=${BATCH:-4096}
# one job (15 GB at batch 4096) so C training fits beside it; the 6 theorems run in turn
for sh in 0; do
  python3 support.py --ckpt ckpts/lf/stage1_a1_seq_s0.pt --model base --stage b --names data/sf/b_names.txt --k 1666667 --stop_at 5 \
    --temperature 1.0 --seed 201 --model_seed 0 --batch $B --max_new 512 --shard 0/1 --out artifacts/sf/b_base_T10_s0 \
    > artifacts/sf/logs/b.log 2>&1 &
done
wait; echo B_DONE
