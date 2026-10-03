#!/usr/bin/env bash
# Addendum 2: group C at r8, sampling k 2,560 (seed 3) vs PUCT-value at its wall clock.  Usage: bash pod/mcts/x10.sh <seed>
source pod/mcts/env.sh
S=$1; CK=ckpts/mcts/la_T1_best12_s${S}_r8.pt; IN=data/mcts/groupC_s$S.jsonl; O=artifacts/mcts/eval_x10/s${S}_r8__C
mkdir -p artifacts/mcts/eval_x10
[ -s $CK ] || hf buckets cp $BK/trajectory/ckpts/tj/ladder/la_T1_best12_s${S}_r8.pt ckpts/mcts/
[ -s ckpts/mcts/value_s${S}_r8.pt ] || hf buckets cp $BK/mcts-a/ckpts/mcts/value_s${S}_r8.pt ckpts/mcts/
[ -s artifacts/mcts/cfg_final.json ] || hf buckets cp $BK/mcts-a/artifacts/mcts/cfg_final.json artifacts/mcts/
md5sum $CK ckpts/mcts/value_s${S}_r8.pt
if [ ! -s ${O}__sample.json ]; then
  nvidia-smi --query-gpu=utilization.gpu --format=csv,noheader,nounits -l 1 > ${O}__sample.util & UP=$!
  python3 state_eval.py --ckpt $CK --in $IN --k 2560 --temperature 0.8 --seed 3 --batch 2048 --max_action 512 --max_steps 96 \
    --lenfield len --out ${O}__sample.jsonl --summary ${O}__sample.json > artifacts/mcts/logs/x10_s${S}_sample.log 2>&1
  kill $UP
fi
W=$(python3 -c "import json;print(json.load(open('${O}__sample.json'))['wall_s'])")
J=$(python3 -c "import json;print(json.dumps(json.load(open('artifacts/mcts/cfg_final.json'))['value']))")
python3 mcts_eval.py --ckpt $CK --in $IN --arm value --value ckpts/mcts/value_s${S}_r8.pt --budget_s $W --seed $S --cfg "$J" \
  --out ${O}__value.jsonl > artifacts/mcts/logs/x10_s${S}_value.log 2>&1
up artifacts/mcts/eval_x10
echo X10_DONE $(ts)
