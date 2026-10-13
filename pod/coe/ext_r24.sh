#!/usr/bin/env bash
# Knockout s1, rounds 21-24 (restores Addendum 6 item 1 after the 08:23 cut; budget re-checked 10:3x), then the r24 plain read.
source pod/coe/env.sh
N=ko_s1; L=artifacts/coe/ladder/la_$N
until [ -e artifacts/coe/markers/extend_$N.done ]; do sleep 60; done
while pgrep -f 'state_ladder_ei.p[y]|state_eval.p[y]|guided_eval.p[y]|state_train.p[y]' > /dev/null; do sleep 30; done
last=$(ls $L/round_*.json | sed 's/.*round_//; s/.json//' | sort -n | tail -1)
ls $L/found_$last.jsonl $L/found_transfer_$last.jsonl $L/alloc_$last.json ckpts/coe/ladder/la_${N}_r$last.pt || { echo "EXT24 FAILED missing resume files"; exit 1; }
if [ "$last" -lt 24 ]; then
  ND_ARM=ko ND_SEED=1 LEAN_GATE_DUMP=artifacts/coe/dump/la_${N}_r21-24.jsonl python3 state_ladder_ei.py --init ckpts/coe/stage1_$N.pt \
    --name la_$N --seed 1 --batch 1024 --train data/coe/train_k12ko.jsonl --heldout data/coe/heldout1000.jsonl \
    --transfer data/coe/transfer_track832.jsonl --outdir artifacts/coe/ladder --ckptdir ckpts/coe/ladder \
    --resume --start_round $((last+1)) --rounds $((24-last)) || { echo "EXT24 FAILED ladder"; exit 1; }
fi
gzip -f artifacts/coe/dump/la_${N}_r21-24.jsonl 2>/dev/null
R=artifacts/coe/eval/r24_${N}_x0
[ -s $R.json ] || python3 state_eval.py --ckpt ckpts/coe/ladder/la_${N}_r24.pt --in data/coe/read1054.jsonl --k 256 --temperature 0.8 \
  --seed 0 --batch 512 --max_action 512 --max_steps 96 --out $R.jsonl --summary $R.json > $R.log 2>&1 && gzip -f $R.jsonl
up artifacts/coe/eval; up artifacts/coe/ladder/la_$N
hf buckets sync artifacts/coe/dump $BK/create-or-elicit/artifacts/coe/dump --include '*.gz' >/dev/null 2>&1
touch artifacts/coe/markers/ext24_$N.done
echo "=== ext_r24 done $N $(date -u +%FT%TZ)"
