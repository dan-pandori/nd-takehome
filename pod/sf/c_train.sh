#!/usr/bin/env bash
# C: bigger base. 8 layers, d 512, 8 heads; otherwise the control's Stage-1 recipe (6,000 x 128, cap 6, lr 1e-3 -> 1e-4, warmup 200).
cd /workspace/nd-takehome; export PATH=$HOME/.elan/bin:$PATH LEAN_GATE_WORKERS=8
S=${SEED:-0}
python3 train.py --data data/p2/train_depth3_f0_a1.jsonl --heldout data/p2/heldout.jsonl --mode lean_seq --steps 6000 --bs 128 \
  --cap 6 --seed $S --n_layer 8 --d 512 --n_head 8 --out ckpts/sf/stage1_big_seq_s$S.pt > artifacts/sf/logs/c_train_s$S.log 2>&1
md5sum ckpts/sf/stage1_big_seq_s$S.pt >> artifacts/sf/logs/c_train_s$S.log
python3 eval_set.py --ckpt ckpts/sf/stage1_big_seq_s$S.pt --in data/p2/heldout.jsonl --out artifacts/sf/c_heldout_greedy_s$S.jsonl \
  --k 1 --temperature 0 --batch 512 --summary artifacts/sf/c_heldout_greedy_s$S.json > artifacts/sf/logs/c_heldout_s$S.log 2>&1
echo C_TRAIN_DONE
