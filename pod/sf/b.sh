#!/usr/bin/env bash
# B: 6 longest survivors (L_true 11/12), base s0, T 1.0, up to 1,666,667 more attempts each, stop at 5. One job per theorem.
cd /workspace/nd-takehome; export PATH=$HOME/.elan/bin:$PATH LEAN_GATE_WORKERS=${LGW:-1}
B=${BATCH:-4096}
for sh in 0 1 2 3 4 5; do
  python3 support.py --ckpt ckpts/lf/stage1_a1_seq_s0.pt --model base --stage b --names data/sf/b_names.txt --k 1666667 --stop_at 5 \
    --temperature 1.0 --seed $((201+sh)) --model_seed 0 --batch $B --max_new 512 --shard $sh/6 --out artifacts/sf/b_base_T10_s0 \
    > artifacts/sf/logs/b_sh$sh.log 2>&1 &
done
wait; echo B_DONE
