#!/usr/bin/env bash
# Certificate top-up (2026-10-13): post.sh sized the per-member attempts for 106 strict members (n = 59.9 K / 106); pooling
# over the 105 FAMILY members (the 106 minus the generated la_transfer_916, which the knockout bases do reach) needs
# 59.9 K / 105.  One more chunk of 1,024 attempts per family member (new sampling seeds) covers it.
# Usage: bash pod/coe/topup.sh <seed> <wait-marker>
source pod/coe/env.sh
S=$1; WAIT=$2; N=ko_s$S; CK=ckpts/coe/stage1_$N.pt
until [ -e artifacts/coe/markers/$WAIT ]; do sleep 60; done
python3 coe/coe_bigk.py --ckpt $CK --in data/coe/read1054.jsonl --names @data/coe/sigma_heldout_family105.txt --n 1024 --chunk 1024 \
  --batch 1024 --stop_successes 1 --seed0 9600 --out artifacts/coe/large/sig105_topup_$N > artifacts/coe/logs/bigk_topup_$N.log 2>&1
up artifacts/coe/large
touch artifacts/coe/markers/topup_$N.done
echo "=== topup done $N $(date -u +%FT%TZ)"
