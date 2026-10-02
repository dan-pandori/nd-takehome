source pod/mcts/env.sh
CK=ckpts/mcts/la_T1_best12_s0_r8.pt
W=$(python3 -c "import json;print(json.load(open('artifacts/mcts/smoke/C_sample.json'))['wall_s'])")
for A in prior value; do
  python3 mcts_eval.py --ckpt $CK --in data/mcts/groupC_s0.jsonl --arm $A --value artifacts/mcts/smoke/value_smoke.pt \
    --budget_s $W --out artifacts/mcts/smoke/C2_$A.jsonl 2>&1 | grep -v "^\[lean" | tail -3 | cut -c1-420
done
