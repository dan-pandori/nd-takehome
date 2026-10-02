#!/usr/bin/env bash
# Smoke (preregistration § 8): s / update and peak memory for one GRPO job, then two jobs on one card; a boundary eval
# timing from one short run with evals.  Usage: bash pod/gb/smoke.sh
source pod/gb/env.sh
CK=ckpts/tj/stage1_best12_s0_b1200.pt
run() { ND_ARM=$1 ND_SEED=0 python3 grpo_state.py --init $CK --name $1 --seed 0 --adv $2 --group 8 --prompts 256 --rounds 8 --k 32 \
          --temperature 0.8 --lr 3e-5 --max_action 256 --max_steps 48 --batch 2048 --lp_batch ${LP:-256} \
          --heldout data/p2/heldout.jsonl --outdir artifacts/gb/smoke --ckptdir ckpts/gb/smoke --steps_log --max_steps_total $3 $4; }
echo "=== alone default $(date -u +%T)"; run smk_default_alone default 6 --no_eval
echo "=== alone unlikely $(date -u +%T)"; run smk_unlikely_alone unlikely 4 --no_eval
echo "=== pair $(date -u +%T)"; run smk_pair_a default 6 --no_eval & run smk_pair_b passk 6 --no_eval; wait
echo "=== end $(date -u +%T)"
up artifacts/gb
