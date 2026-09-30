#!/usr/bin/env bash
# GPU smoke (code phase, <= 30 min): grpo_state.py on SN-cap12 s0 at the pre-registered settings (256 theorems x G 8,
# decode batch 2,048, lr 3e-5), a few updates per advantage variant, no boundary evals (EI's eval cost is known).
# Measures s/update (sampling + Lean vs update), peak memory, groups with variance.  Usage: bash pod/gs/smoke.sh
source pod/gs/env.sh
CK=ckpts/sc12/stage1_SN12_s0.pt
for spec in "default 8" "unlikely 4" "passk 4" "distinct 4"; do
  set -- $spec; A=$1; n=$2
  echo "=== $A $n updates $(date -u +%FT%TZ)"
  ND_ARM=smoke_$A ND_SEED=0 python3 grpo_state.py --init $CK --name smoke_$A --seed 0 --adv $A --lr 3e-5 --prompts 256 --group 8 \
    --batch 2048 --max_steps_total $n --no_eval --steps_log --outdir artifacts/grpo_state --ckptdir ckpts/grpo_state \
    --heldout data/p2/heldout.jsonl > artifacts/grpo_state/logs/smoke_$A.log 2>&1 || echo "FAILED $A"
  tail -3 artifacts/grpo_state/logs/smoke_$A.log
done
up artifacts/grpo_state
echo SMOKE_DONE $(date -u +%FT%TZ)
