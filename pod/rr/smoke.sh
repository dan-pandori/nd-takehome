#!/usr/bin/env bash
# results-registry smoke run (pre-registered): Stage-1 for 300 steps (throwaway model), one greedy held-out eval,
# one tiny coverage job, two tiny EI rounds. Every script records to the registry; every checkpoint uploads on save.
cd /workspace/nd-takehome
export ND_RUN_ID=results-registry OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 PATH=$HOME/.elan/bin:$PATH ND_REGISTRY_SYNC_S=30
T=artifacts/rr/timing.txt; : > $T
t() { local s=$(date +%s); "$@"; local rc=$?; echo "$(date -u +%FT%TZ) rc=$rc $(( $(date +%s) - s ))s $*" >> $T; return $rc; }
t python3 train.py --data data/p2/train_depth3_f0_a1.jsonl --heldout data/p2/heldout.jsonl --mode lean_seq --cap 6 \
  --steps 300 --log_every 100 --ckpt_every 150 --state_at 150 --seed 0 --out ckpts/rr/smoke_s0.pt \
  --metrics artifacts/rr/smoke_train.jsonl > artifacts/rr/train.log 2>&1 || exit 1
t python3 eval_set.py --ckpt ckpts/rr/smoke_s0.pt --in data/p2/heldout.jsonl --limit 500 --k 1 --temperature 0 \
  --out artifacts/rr/heldout_greedy.jsonl --summary artifacts/rr/heldout_greedy.json > artifacts/rr/eval.log 2>&1
t python3 coverage.py --ckpt ckpts/rr/smoke_s0.pt --in data/ladder/transfer.jsonl --limit 2 --k 256 --batch 256 \
  --max_new 288 --out artifacts/rr/cov_smoke > artifacts/rr/cov.log 2>&1
t python3 expert_iter.py --init ckpts/rr/smoke_s0.pt --name rr/ei_smoke_s0 --targets data/rr_targets40.jsonl \
  --transfer data/rr_transfer40.jsonl --heldout data/rr_heldout200.jsonl --train data/p2/train_depth3_f0_a1.jsonl \
  --rounds 2 --k 8 --ft_steps 30 --retain 500 --seed 0 --batch 1024 > artifacts/rr/ei.log 2>&1
python3 -c "import torch; print('peak GiB n/a (separate processes)')" >/dev/null
touch artifacts/rr/smoke.done
