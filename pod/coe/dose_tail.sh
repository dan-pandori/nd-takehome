#!/usr/bin/env bash
# Budget trim for the 1 % dose arm (log 2026-10-13 04:2x): after the r16 PLAIN read (x0) stop the reader (no r16 guided g0 /
# redraw x1 reads), then the post steps without standard-A sampling: timing read (c_base), coe_kpod (K_train(16)), and the
# along-the-ladder scoring of the known sigma proofs.  Usage: bash pod/coe/dose_tail.sh <seed>
source pod/coe/env.sh
S=$1; N=dose1_s$S; CK=ckpts/coe/stage1_$N.pt
mkdir -p artifacts/coe/timing artifacts/coe/budget artifacts/coe/large artifacts/coe/score
until [ -s artifacts/coe/eval/r16_${N}_x0.json ]; do sleep 60; done
pkill -f 'pod/coe/reade[r].sh'; sleep 3; pkill -f 'guided_eval.p[y].*r16_dose1'; pkill -f 'state_eval.p[y].*r16_dose1_s[0-9]_x1'
touch artifacts/coe/markers/reads_$N.done
up artifacts/coe/eval
while pgrep -f 'state_ladder_ei.p[y]|state_eval.p[y]|guided_eval.p[y]' > /dev/null; do sleep 30; done
T=artifacts/coe/timing/A40_pend_${N}_b1024
[ -s $T.json ] || python3 state_eval.py --ckpt $CK --in data/coe/r322.jsonl --k 256 --temperature 0.8 --seed 0 --batch 1024 \
  --max_action 512 --max_steps 96 --summary $T.json > $T.log 2>&1
python3 coe/coe_kpod.py --arm dose1 --seed $S > artifacts/coe/budget/k_${N}.txt 2>&1
if [ ! -s artifacts/coe/score/rounds_$N/r16.jsonl.gz ]; then
  mkdir -p artifacts/coe/score/rounds_$N
  { echo "pend $CK"; for R in 4 8 12 16; do echo "r$R ckpts/coe/ladder/la_${N}_r$R.pt"; done; } > artifacts/coe/score/rounds_$N/ckpts.txt
  gunzip -kf data/coe/known_targets_heldout.jsonl.gz
  python3 coe/cd_score.py --targets data/coe/known_targets_heldout.jsonl --ckpts artifacts/coe/score/rounds_$N/ckpts.txt \
    --out artifacts/coe/score/rounds_$N --nbases 1 > artifacts/coe/logs/score_rounds_$N.log 2>&1
  gzip -f artifacts/coe/score/rounds_$N/*.jsonl
fi
for d in artifacts/coe/timing artifacts/coe/budget artifacts/coe/score artifacts/coe/eval artifacts/create-or-elicit; do up $d; done
up artifacts/coe/ladder/la_$N
hf buckets sync artifacts/coe/dump $BK/create-or-elicit/artifacts/coe/dump --include '*.gz' >/dev/null 2>&1
touch artifacts/coe/markers/post_$N.done
echo "=== dose_tail done $N $(date -u +%FT%TZ)"
