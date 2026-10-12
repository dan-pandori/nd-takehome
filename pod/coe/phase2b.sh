#!/usr/bin/env bash
# Phase 2b (Addendum 4): convergence (32 MH steps per block), positive control (17 rarely-solved theorems), alpha 1.5.
source pod/coe/env.sh
mkdir -p artifacts/coe/power ckpts/coe/old
CK=ckpts/coe/old/stage1_best12_s0_b1200.pt
[ -s $CK ] || hf buckets cp $BK/trajectory/ckpts/tj/stage1_best12_s0_b1200.pt $CK >/dev/null 2>&1
md5sum $CK
P=artifacts/coe/power/p2b
pw() {   # <names> <alpha> <n_mcmc> <tag>
  [ -s ${P}_$4.json ] || python3 coe/power_sample.py --ckpt $CK --in data/coe/read1054.jsonl --names @$1 --alpha $2 --chains 32 --block 4 \
    --n_mcmc $3 --batch 1024 --seed 2 --out ${P}_$4
}
pl() {   # <names> <T> <budget tag> <tag>
  [ -s ${P}_$4.json ] || python3 coe/power_sample.py --ckpt $CK --in data/coe/read1054.jsonl --names @$1 --mode plain --temperature $2 \
    --batch 1024 --seed 2 --budget_from ${P}_$3.json --out ${P}_$4
}
pw data/coe/phase2_cm_ktrain_s0.txt 4 32 cm_a4_m32
[ -s ${P}_pilot_a4_m32.json ] || python3 coe/power_sample.py --ckpt $CK --in data/coe/power_pilot32.jsonl --alpha 4 --chains 16 --block 4 \
  --n_mcmc 32 --batch 1024 --seed 0 --out ${P}_pilot_a4_m32
pw data/coe/phase2b_posctl_s0.txt 4 8 pc_a4
pl data/coe/phase2b_posctl_s0.txt 0.8 pc_a4 pc_plainT0.8
pl data/coe/phase2b_posctl_s0.txt 1.0 pc_a4 pc_plainT1.0
pw data/coe/phase2b_posctl_s0.txt 1.5 8 pc_a1.5
pw data/coe/phase2_cm_ktrain_s0.txt 1.5 8 cm_a1.5
up artifacts/coe/power
echo PHASE2B_DONE
