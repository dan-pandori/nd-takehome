#!/usr/bin/env bash
# One GRPO ladder of the experiment (preregistration/grpo-state.md § 3), for the queued experiment run.
# Usage: bash pod/gs/grpo_seed.sh <adv: default|unlikely|passk|distinct> <seed>
# Needs ckpts/sc12/stage1_SN12_s<seed>.pt (state-cap12 bucket, or trained with state_train.py as in pod/sc12/sn_seed.sh).
source pod/gs/env.sh
A=$1; S=$2; CK=ckpts/sc12/stage1_SN12_s$S.pt; N=grpo_${A}_SN12_s$S
[ -s $CK ] || hf buckets cp hf://buckets/dan-pandori/nd-rl/state-cap12/ckpts/sc12/stage1_SN12_s$S.pt $CK || exit 1
EXTRA=""; [ $A = unlikely ] && EXTRA="--beta_rank 0.25"; [ $A = passk ] && EXTRA="--passk_k 4"; [ $A = distinct ] && EXTRA="--bonus 0.5"
if [ ! -s artifacts/grpo_state/$N/round_8.json ]; then
  echo "=== $N $(date -u +%FT%TZ)"
  ND_ARM=$N ND_SEED=$S python3 grpo_state.py --init $CK --name $N --seed $S --adv $A $EXTRA --lr 3e-5 --group 8 --prompts 256 \
    --batch 2048 --heldout data/p2/heldout.jsonl --outdir artifacts/grpo_state --ckptdir ckpts/grpo_state --steps_log \
    > artifacts/grpo_state/logs/$N.log 2>&1 || { echo "FAILED $N"; exit 1; }
fi
up artifacts/grpo_state; up artifacts/grpo-state
echo "DONE $N $(date -u +%FT%TZ)"
