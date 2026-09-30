#!/usr/bin/env bash
# One M2 grid cell: Stage-1 (noise-floor control recipe, --impl fast) at init seed $1, data seed $2, then held-out greedy.
# optional 3rd arg: replicate tag (same seeds, re-run)
set -e; I=$1; D=$2; C=i${I}_d${D}${3:+_$3}; O=artifacts/lit-measures/m2
[ -f $O/heldout_$C.json ] && { echo "have $C"; exit 0; }
grep -q '^saved ' $O/logs/train_$C.log 2>/dev/null && [ -f ckpts/lm/stage1_$C.pt ] || \
{ rm -f $O/metrics_$C.jsonl; python3 train.py --data data/nf/train_p1.jsonl --heldout data/p2/heldout.jsonl --mode lean_seq --steps 6000 --bs 128 \
  --cap 6 --seed $I --data_seed $D --impl fast --out ckpts/lm/stage1_$C.pt --metrics $O/metrics_$C.jsonl > $O/logs/train_$C.log 2>&1; }
python3 eval_set.py --ckpt ckpts/lm/stage1_$C.pt --in data/p2/heldout.jsonl --out $O/heldout_$C.jsonl --k 1 --temperature 0 \
  --summary $O/heldout_$C.json.tmp > $O/logs/heldout_$C.log 2>&1
mv $O/heldout_$C.json.tmp $O/heldout_$C.json
