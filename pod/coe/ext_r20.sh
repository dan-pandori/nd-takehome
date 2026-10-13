#!/usr/bin/env bash
# Budget cut (log 2026-10-13 08:2x): knockout s1's extension stops after round 20 (not 24).  Waits for round_20.json, stops the
# ladder, reads r20 (plain k 256 on read1054), uploads.  Replaces extend_k1.sh (its parent shell is killed; the ladder child
# keeps running until round 20 completes).
source pod/coe/env.sh
N=ko_s1; L=artifacts/coe/ladder/la_$N
until [ -s $L/round_20.json ] && [ -s ckpts/coe/ladder/la_${N}_r20.pt ]; do sleep 60; done
sleep 30
pkill -f 'state_ladder_ei.p[y]'; sleep 10; pkill -f 'state_train.p[y]'
R=artifacts/coe/eval/r20_${N}_x0
[ -s $R.json ] || python3 state_eval.py --ckpt ckpts/coe/ladder/la_${N}_r20.pt --in data/coe/read1054.jsonl --k 256 --temperature 0.8 \
  --seed 0 --batch 512 --max_action 512 --max_steps 96 --out $R.jsonl --summary $R.json > $R.log 2>&1 && gzip -f $R.jsonl
gzip -f artifacts/coe/dump/la_${N}_r17-24.jsonl 2>/dev/null
up artifacts/coe/eval; up artifacts/coe/ladder/la_$N
hf buckets sync artifacts/coe/dump $BK/create-or-elicit/artifacts/coe/dump --include '*.gz' >/dev/null 2>&1
touch artifacts/coe/markers/extend_$N.done
echo "=== ext_r20 done $N $(date -u +%FT%TZ)"
