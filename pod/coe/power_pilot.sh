#!/usr/bin/env bash
# Phase 2 pilot (development data only: 32 random non-schema rl_targets): self-test, then power sampling of trajectory's
# pend s0 at alpha 4 (block 4 steps, 8 MH steps per block, 16 chains) and plain T 0.8 / T 1.0 at matched decoded tokens.
source pod/coe/env.sh
CK=ckpts/coe/old/stage1_best12_s0_b1200.pt
[ -s $CK ] || hf buckets cp $BK/trajectory/ckpts/tj/stage1_best12_s0_b1200.pt $CK >/dev/null 2>&1
mkdir -p artifacts/coe/power
python3 coe/power_sample.py --selftest --ckpt $CK --in data/coe/power_pilot32.jsonl
python3 coe/power_sample.py --ckpt $CK --in data/coe/power_pilot32.jsonl --alpha 4 --chains 16 --block 4 --n_mcmc 8 --batch 1024 \
  --out artifacts/coe/power/pilot_a4_pend_s0
for T in 0.8 1.0; do
  python3 coe/power_sample.py --ckpt $CK --in data/coe/power_pilot32.jsonl --mode plain --temperature $T --batch 1024 \
    --budget_from artifacts/coe/power/pilot_a4_pend_s0.json --out artifacts/coe/power/pilot_plainT${T}_pend_s0
done
up artifacts/coe/power
echo PILOT_DONE
