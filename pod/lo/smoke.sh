#!/usr/bin/env bash
# End-to-end smoke test of the lean_check-only loop for both formats: 300-step Stage-1, pass@4 on 300 held-out, one EI round on 100 targets.
cd /workspace/nd-takehome; export PATH=$HOME/.elan/bin:$PATH LEAN_CHECK_WORKERS=12 OMP_NUM_THREADS=4 PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
mkdir -p artifacts/lo/smoke ckpts/lo artifacts/lo/logs
head -n 100 data/p2/targets_depth3.jsonl > artifacts/lo/smoke/targets100.jsonl; head -n 50 data/p2/transfer_depth3.jsonl > artifacts/lo/smoke/transfer50.jsonl; head -n 200 data/p2/heldout.jsonl > artifacts/lo/smoke/heldout200.jsonl
{
for m in lean_free lean_seq; do
  echo "=== $m $(date -u +%T)"
  python3 train.py --data data/train.jsonl --heldout data/heldout.jsonl --mode $m --steps 300 --bs 128 --out ckpts/lo/smoke_$m.pt --cap 6 --seed 0 2>&1 | tail -n 4
  LEAN_GATE_LOG=artifacts/lo/smoke/gate_eval_$m.jsonl python3 eval_set.py --ckpt ckpts/lo/smoke_$m.pt --in data/heldout.jsonl --out artifacts/lo/smoke/eval_$m.jsonl --k 4 --temperature 0.8 --limit 300 --batch 512 --summary artifacts/lo/smoke/eval_$m.json 2>&1 | tail -n 12
  LEAN_GATE_LOG=artifacts/lo/smoke/gate_ei_$m.jsonl python3 expert_iter.py --init ckpts/lo/smoke_$m.pt --name lo/smoke_ei_$m --targets artifacts/lo/smoke/targets100.jsonl --transfer artifacts/lo/smoke/transfer50.jsonl --heldout artifacts/lo/smoke/heldout200.jsonl --train data/p2/train_depth3_f0_a1.jsonl --rounds 2 --k 8 --temperature 0.8 --batch 768 --seed 0 2>&1 | grep -v "^\[lean_gate\]" | tail -n 25
  echo "=== $m done $(date -u +%T)"
done
echo SMOKE_DONE
} > artifacts/lo/logs/smoke.log 2>&1
