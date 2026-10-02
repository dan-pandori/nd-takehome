#!/usr/bin/env bash
# One GRPO ladder from trajectory's base checkpoint.  Usage: bash pod/gb/grpo.sh <adv> <seed> [extra grpo_state args]
# Pre-registered settings (preregistration/grpo-best.md § 3); LP (pairs per chunk) and B (decode batch) from the smoke.
source pod/gb/env.sh
ADV=$1; S=$2; shift 2; N=gb_${ADV}_s$S; B=${B:-2048}; LP=${LP:-256}
CK=ckpts/tj/stage1_best12_s${S}_b1200.pt
get trajectory/$CK $CK || { echo "no base $CK"; exit 1; }
EXTRA=""; [ "$ADV" = unlikely ] && EXTRA="--beta_rank 0.25"; [ "$ADV" = passk ] && EXTRA="--passk_k 4"; [ "$ADV" = distinct ] && EXTRA="--bonus 0.5"
echo "=== $N start $(date -u +%FT%TZ) base md5 $(md5sum < $CK | cut -c1-8)"
ND_ARM=$N ND_SEED=$S python3 grpo_state.py --init $CK --name $N --seed $S --adv $ADV $EXTRA --group 8 --prompts 256 \
  --rounds 8 --k 32 --temperature 0.8 --lr 3e-5 --max_action 256 --max_steps 48 --batch $B --lp_batch $LP \
  --heldout data/p2/heldout.jsonl --outdir artifacts/gb --ckptdir ckpts/gb --steps_log "$@"
rc=$?
echo "=== $N end $(date -u +%FT%TZ) rc $rc"
up artifacts/gb
exit $rc
