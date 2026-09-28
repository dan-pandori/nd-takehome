#!/usr/bin/env bash
# First timing pass: 1,000 steps each of fast (packed), fast --no_pack, legacy; seed 0; with --val_bins every 200.
cd /workspace/nd-takehome; export OMP_NUM_THREADS=4
D=data/p2/train_depth3_f0_a1.jsonl; H=data/p2/heldout.jsonl; C="--mode lean_seq --steps ${STEPS:-1000} --bs 128 --cap 6 --seed 0 --val_bins --log_every 200"
TORCH_LOGS=recompiles python3 train.py --data $D --heldout $H $C --impl fast --out ckpts/fs/b1_fast.pt --metrics artifacts/fs/b1_fast.jsonl > artifacts/fs/logs/b1_fast.log 2>&1

TORCH_LOGS=recompiles python3 train.py --data $D --heldout $H $C --impl fast --no_pack --out ckpts/fs/b1_nopack.pt --metrics artifacts/fs/b1_nopack.jsonl > artifacts/fs/logs/b1_nopack.log 2>&1

touch artifacts/fs/b1.done
