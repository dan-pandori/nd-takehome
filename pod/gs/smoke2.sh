#!/usr/bin/env bash
# GPU smoke 2 (after the review fixes): the full boundary path (transfer pass@k, greedy transfer / held-out, found files,
# registry rows) on subsets: 64 targets, 64 transfer, 200 held-out; 2 round-equivalents of 1 update each (2 x 32 x 64 =
# 4,096 rollouts); default with KL 0.02 and unlikely.  Usage: bash pod/gs/smoke2.sh
source pod/gs/env.sh
mkdir -p data/gs
head -64 data/ladder/rl_targets.jsonl > data/gs/targets64.jsonl
head -64 data/ladder/transfer.jsonl > data/gs/transfer64.jsonl
head -200 data/p2/heldout.jsonl > data/gs/heldout200.jsonl
CK=ckpts/sc12/stage1_SN12_s0.pt
for spec in "default --kl 0.02" "unlikely --beta_rank 0.25"; do
  set -- $spec; A=$1; shift
  echo "=== smoke2 $A $(date -u +%FT%TZ)"
  ND_ARM=smoke2_$A ND_SEED=0 python3 grpo_state.py --init $CK --name smoke2_$A --seed 0 --adv $A "$@" --lr 3e-5 --prompts 256 --group 8 \
    --batch 2048 --rounds 2 --k 32 --targets data/gs/targets64.jsonl --transfer data/gs/transfer64.jsonl --heldout data/gs/heldout200.jsonl \
    --steps_log --outdir artifacts/grpo_state --ckptdir ckpts/grpo_state > artifacts/grpo_state/logs/smoke2_$A.log 2>&1 || echo "FAILED $A"
  grep -E "^\[smoke2|^step|DONE|Error" artifacts/grpo_state/logs/smoke2_$A.log | tail -8
done
up artifacts/grpo_state; up artifacts/grpo-state
echo SMOKE2_DONE $(date -u +%FT%TZ)
