#!/usr/bin/env bash
# Addendum 6 item 1: knockout s1, rounds 17-24 (resume of the 16-round ladder, same settings), then a plain r24 read.
source pod/coe/env.sh
N=ko_s1; L=artifacts/coe/ladder/la_$N
until [ -e artifacts/coe/markers/p3a_$N.done ]; do sleep 60; done
while pgrep -f 'state_ladder_ei.p[y]|state_eval.p[y]|guided_eval.p[y]|coe_bigk.p[y]|state_train.p[y]' > /dev/null; do sleep 30; done
ls $L/found_16.jsonl $L/found_transfer_16.jsonl $L/alloc_16.json $L/round_16.json ckpts/coe/ladder/la_${N}_r16.pt || { echo "EXTEND FAILED missing resume files"; exit 1; }
cp $L/args.json $L/args_r1-16.json
last=$(ls $L/round_*.json | sed 's/.*round_//; s/.json//' | sort -n | tail -1)
if [ "$last" -lt 24 ]; then
  ND_ARM=ko ND_SEED=1 LEAN_GATE_DUMP=artifacts/coe/dump/la_${N}_r17-24.jsonl python3 state_ladder_ei.py --init ckpts/coe/stage1_$N.pt \
    --name la_$N --seed 1 --batch 1024 --train data/coe/train_k12ko.jsonl --heldout data/coe/heldout1000.jsonl \
    --transfer data/coe/transfer_track832.jsonl --outdir artifacts/coe/ladder --ckptdir ckpts/coe/ladder \
    --resume --start_round $((last+1)) --rounds $((24-last)) || { echo "EXTEND FAILED ladder"; exit 1; }
fi
gzip -f artifacts/coe/dump/la_${N}_r17-24.jsonl 2>/dev/null
R=artifacts/coe/eval/r24_${N}_x0
[ -s $R.json ] || python3 state_eval.py --ckpt ckpts/coe/ladder/la_${N}_r24.pt --in data/coe/read1054.jsonl --k 256 --temperature 0.8 \
  --seed 0 --batch 512 --max_action 512 --max_steps 96 --out $R.jsonl --summary $R.json > $R.log 2>&1 && gzip -f $R.jsonl
up artifacts/coe/eval; up artifacts/coe/ladder/la_$N
hf buckets sync artifacts/coe/dump $BK/create-or-elicit/artifacts/coe/dump --include '*.gz' >/dev/null 2>&1
touch artifacts/coe/markers/extend_$N.done
echo "=== extend done $N $(date -u +%FT%TZ)"
