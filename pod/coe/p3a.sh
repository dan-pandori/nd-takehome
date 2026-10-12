#!/usr/bin/env bash
# Phase 3a (Addendum 6): one extra EI-style round from this knockout seed's r16 checkpoint, seeded (with knockout s1's base's
# free-sigma proof of la_transfer_916) and control (without); then plain k 256 reads of the other 105 strict held-out members.
# Runs after the seed's post job.  Usage: bash pod/coe/p3a.sh <seed>
source pod/coe/env.sh
S=$1; N=ko_s$S; L=artifacts/coe/ladder/la_$N; CK=ckpts/coe/ladder/la_${N}_r16.pt
until [ -e artifacts/coe/markers/post_$N.done ]; do sleep 60; done
while pgrep -f 'state_ladder_ei.p[y]|state_eval.p[y]|guided_eval.p[y]|coe_bigk.p[y]' > /dev/null; do sleep 30; done
mkdir -p ckpts/coe/p3a artifacts/coe/p3a
grep -h '"la_transfer_916"\|la_transfer_916' data/coe/phase3a_seed.jsonl > /dev/null || { echo "no seed proof"; exit 1; }
for ARMX in control seeded; do
  O=ckpts/coe/p3a/${N}_$ARMX.pt
  [ -s $O ] || ND_ARM=p3a_$ARMX ND_SEED=$S python3 coe/coe_seeded_round.py --ladder $L --init $CK --train data/coe/train_k12ko.jsonl \
    --seed_proofs data/coe/phase3a_seed.jsonl --arm $ARMX --out $O > artifacts/coe/logs/p3a_${N}_$ARMX.log 2>&1 || { echo "P3A FAILED $ARMX"; exit 1; }
  python3 -c "
import json
names=set(open('data/coe/sigma_heldout_strict_no916.txt').read().split())
with open('data/coe/p3a_read105.jsonl','w') as f:
    for l in open('data/coe/read1054.jsonl'):
        if json.loads(l)['name'] in names: f.write(l)
"
  R=artifacts/coe/p3a/${N}_${ARMX}_x0
  [ -s $R.json ] || python3 state_eval.py --ckpt $O --in data/coe/p3a_read105.jsonl --k 256 --temperature 0.8 --seed 0 --batch 512 \
    --max_action 512 --max_steps 96 --out $R.jsonl --summary $R.json > $R.log 2>&1 && gzip -f $R.jsonl
done
rm -f ckpts/coe/p3a/*_mix.jsonl
up artifacts/coe/p3a
touch artifacts/coe/markers/p3a_$N.done
echo "=== p3a done $N $(date -u +%FT%TZ)"
