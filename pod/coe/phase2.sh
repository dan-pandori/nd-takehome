#!/usr/bin/env bash
# Phase 2 production (Addendum 3): power sampling (alpha 4 and 2) + plain T 0.8 / 1.0 at matched decoded tokens.
source pod/coe/env.sh
mkdir -p artifacts/coe/power ckpts/coe/old
for S in 0 1; do
  [ -s ckpts/coe/old/stage1_best12_s${S}_b1200.pt ] || hf buckets cp $BK/trajectory/ckpts/tj/stage1_best12_s${S}_b1200.pt ckpts/coe/old/stage1_best12_s${S}_b1200.pt >/dev/null 2>&1
  [ -s ckpts/coe/stage1_ko_s${S}.pt ] || hf buckets cp $BK/create-or-elicit/ckpts/coe/stage1_ko_s${S}.pt ckpts/coe/stage1_ko_s${S}.pt >/dev/null 2>&1
done
md5sum ckpts/coe/old/*.pt ckpts/coe/stage1_ko_s*.pt
run() {   # <ckpt> <names file> <tag>
  for A in 4 2; do
    O=artifacts/coe/power/p2_${3}_a$A
    [ -s $O.json ] || python3 coe/power_sample.py --ckpt $1 --in data/coe/read1054.jsonl --names @$2 --alpha $A --chains 32 --block 4 \
      --n_mcmc 8 --batch 1024 --seed 1 --out $O
    if [ "$A" = 4 ]; then
      for T in 0.8 1.0; do
        P=artifacts/coe/power/p2_${3}_plainT${T}
        [ -s $P.json ] || python3 coe/power_sample.py --ckpt $1 --in data/coe/read1054.jsonl --names @$2 --mode plain --temperature $T \
          --batch 1024 --seed 1 --budget_from $O.json --out $P
      done
    fi
    up artifacts/coe/power
  done
}
run ckpts/coe/old/stage1_best12_s0_b1200.pt data/coe/phase2_cm_ktrain_s0.txt full_s0
run ckpts/coe/old/stage1_best12_s1_b1200.pt data/coe/phase2_cm_ktrain_s1.txt full_s1
run ckpts/coe/stage1_ko_s0.pt data/coe/sigma_heldout_strict.txt ko_s0
run ckpts/coe/stage1_ko_s1.pt data/coe/sigma_heldout_strict.txt ko_s1
up artifacts/create-or-elicit/registry
echo PHASE2_DONE
