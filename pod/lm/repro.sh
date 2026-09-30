#!/usr/bin/env bash
# Default reproduction: new trainer with the default data_seed vs origin/dan's trainer (/workspace/orig), 300 steps,
# legacy and --impl fast, every 10 steps; then a full legacy 6,000-step run of --seed 0 on train_p1 to compare with
# noise-floor's stage1_p1_s0 log.
O=artifacts/lit-measures/m2/repro; mkdir -p $O
A="--data data/nf/train_p1.jsonl --heldout data/p2/heldout.jsonl --mode lean_seq --bs 128 --cap 6 --seed 0 --log_every 10"
for impl in legacy fast; do
  X=""; [ $impl = fast ] && X="--impl fast"
  ND_OFFLINE=1 python3 train.py $A $X --steps 300 --out /tmp/new_$impl.pt --metrics $O/new_$impl.jsonl > $O/new_$impl.log 2>&1
  ND_OFFLINE=1 python3 train.py $A $X --steps 300 --data_seed 0 --out /tmp/newx_$impl.pt --metrics $O/newx_$impl.jsonl > $O/newx_$impl.log 2>&1
  (cd /workspace/orig && ND_OFFLINE=1 python3 train.py $A $X --steps 300 --out /tmp/orig_$impl.pt \
     --metrics /workspace/nd-takehome/$O/orig_$impl.jsonl > /workspace/nd-takehome/$O/orig_$impl.log 2>&1)
done
python3 train.py --data data/nf/train_p1.jsonl --heldout data/p2/heldout.jsonl --mode lean_seq --steps 6000 --bs 128 --cap 6 \
  --seed 0 --out ckpts/lm/repro_legacy_p1_s0.pt --metrics $O/full_legacy_p1_s0.jsonl > $O/full_legacy_p1_s0.log 2>&1
echo REPRO_DONE
