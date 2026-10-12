#!/usr/bin/env bash
# After a seed's ladder and reads: (1) the base's per-attempt cost on the 322 alone on the GPU (batch 1,024, k 256) -- the
# uniform-allocation c_base of K_train; (2) large-k plain sampling of the base (coe_bigk.py, every success kept with its
# multiplicity): on the 178 sigma-covered held-out classical members (knockout seeds: the certificate) and on the theorems of
# the 322 that r16 solves and the base failed in its 512 read attempts (standard A, every new seed).
# Usage: bash pod/coe/post.sh <full|ko> <seed> <n per sigma member> <n per standard-A theorem> [names file for standard A]
source pod/coe/env.sh
ARM=$1; S=$2; NSIG=$3; NA=$4; NAMES=$5; N=${ARM}_s${S}; CK=ckpts/coe/stage1_$N.pt
until [ -e artifacts/coe/markers/reads_$N.done ]; do sleep 60; done
while pgrep -f 'state_ladder_ei.p[y]|state_eval.p[y]|guided_eval.p[y]' > /dev/null; do sleep 30; done
T=artifacts/coe/timing/A40_pend_${N}_b1024
[ -s $T.json ] || python3 state_eval.py --ckpt $CK --in data/coe/r322.jsonl --k 256 --temperature 0.8 --seed 0 --batch 1024 \
  --max_action 512 --max_steps 96 --summary $T.json > $T.log 2>&1
up artifacts/coe/timing
if [ "$ARM" = ko ] && [ "$NSIG" -gt 0 ]; then
  python3 coe/coe_bigk.py --ckpt $CK --in data/coe/read1054.jsonl --names @data/coe/sigma_heldout178.txt --n $NSIG --chunk 1024 \
    --batch 1024 --stop_successes 1 --seed0 9000 --out artifacts/coe/large/sig178_$N > artifacts/coe/logs/bigk_sig_$N.log 2>&1
  up artifacts/coe/large
fi
if [ -n "$NAMES" ] && [ "$NA" -gt 0 ]; then
  python3 coe/coe_bigk.py --ckpt $CK --in data/coe/read1054.jsonl --names @$NAMES --n $NA --chunk 2048 \
    --batch 1024 --stop_successes 10 --seed0 9100 --out artifacts/coe/large/stdA_$N > artifacts/coe/logs/bigk_stdA_$N.log 2>&1
  up artifacts/coe/large
fi
touch artifacts/coe/markers/post_$N.done
echo "=== post done $N $(date -u +%FT%TZ)"
