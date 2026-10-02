#!/usr/bin/env bash
# GPU smoke test (<= 20 min): small value data + head on s0 r8, then group C s0 r8: sampling, prior, value (default cfg).
source pod/mcts/env.sh
CK=ckpts/mcts/la_T1_best12_s0_r8.pt
echo "=== vdata $(ts)"
python3 mcts_value_data.py --ckpt $CK --n_targets 300 --gen data/kh/train_k12.jsonl --n_gen 100 --k 16 \
  --out artifacts/mcts/smoke/vdata_smoke.pt || exit 1
echo "=== train $(ts)"
python3 mcts_value_train.py --data artifacts/mcts/smoke/vdata_smoke.pt --out artifacts/mcts/smoke/value_smoke.pt \
  --report artifacts/mcts/smoke/value_smoke.json || exit 1
echo "=== sample $(ts)"
python3 state_eval.py --ckpt $CK --in data/mcts/groupC_s0.jsonl --k 256 --temperature 0.8 --seed 2 --batch 2048 \
  --max_action 512 --max_steps 96 --lenfield len --out artifacts/mcts/smoke/C_sample.jsonl --summary artifacts/mcts/smoke/C_sample.json 2>&1 | tail -3
W=$(python3 -c "import json;print(json.load(open('artifacts/mcts/smoke/C_sample.json'))['wall_s'])")
for A in prior value; do
  echo "=== $A budget $W $(ts)"
  python3 mcts_eval.py --ckpt $CK --in data/mcts/groupC_s0.jsonl --arm $A --value artifacts/mcts/smoke/value_smoke.pt \
    --budget_s $W --out artifacts/mcts/smoke/C_$A.jsonl 2>&1 | tail -4
done
echo "=== end $(ts)"
