#!/usr/bin/env bash
# After the main sweep: mutation checks with the tightened translator, and the minlen oracle proofs.
cd /home/dan/work/run1-lean; export PATH=$HOME/.elan/bin:$PATH
until grep -q "SWEEP DONE" artifacts/r1/agree_sweep.log; do sleep 30; done
echo "$(date -u +%T) start mutations v2"
python3 nd2lean.py --mutate data/heldout.jsonl --n 2000 --seed 0 --out artifacts/r1/agree_mut_heldout_v2.jsonl --procs 2 --batch 50 2>&1 | tail -1
python3 nd2lean.py --mutate data/rl_targets.jsonl --n 2000 --seed 1 --out artifacts/r1/agree_mut_rl_targets_v2.jsonl --procs 2 --batch 50 2>&1 | tail -1
python3 nd2lean.py --check artifacts/minlen_transfer.jsonl --out artifacts/r1/agree_minlen_transfer.jsonl --procs 2 --batch 100 2>&1 | tail -1
python3 nd2lean.py --check artifacts/minlen_val36.jsonl --out artifacts/r1/agree_minlen_val36.jsonl --procs 2 --batch 100 2>&1 | tail -1
echo "$(date -u +%T) SWEEP2 DONE"
