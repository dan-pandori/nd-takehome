#!/usr/bin/env bash
# After main.sh: one full 6,000-step legacy model alone on the A40 (the clean per-model baseline), then gpubench (TAG=a40).
cd /workspace/nd-takehome; export OMP_NUM_THREADS=4
D=data/p2/train_depth3_f0_a1.jsonl; H=data/p2/heldout.jsonl
t=$(date +%s.%N); rm -f artifacts/fs/m_legfull_s0.jsonl
python3 train.py --data $D --heldout $H --mode lean_seq --bs 128 --lr 1e-3 --min_lr 1e-4 --warmup 200 --cap 6 --val_bins --log_every 200 \
  --steps 6000 --seed 0 --impl legacy --out ckpts/fs/legfull_s0.pt --metrics artifacts/fs/m_legfull_s0.jsonl > artifacts/fs/logs/legfull_s0.log 2>&1
echo "{\"wave\": \"legfull\", \"impl\": \"legacy\", \"steps\": 6000, \"seeds\": \"0\", \"n\": 1, \"wall_s\": $(python3 -c "import time; print(round(time.time() - $t, 2))")}" >> artifacts/fs/waves.jsonl
TAG=a40 bash pod/fs/gpubench.sh
touch artifacts/fs/a40more.done
