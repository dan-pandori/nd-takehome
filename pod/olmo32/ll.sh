#!/usr/bin/env bash
# ll.sh: likelihood check (pre-registration, Reported quantities): dpo's per-token log-likelihood of every rl-credited
# RL-checkpoint solution on aime2025_28, of dpo's own there, and of a reference set of dpo's own correct solutions.
cd /workspace/nd-takehome; A=artifacts/olmo32; mkdir -p $A/ll
echo "JOB_START L_dpo $(date -u +%FT%TZ)"
python olmo32/ll_items.py $A/ll/items.jsonl aime2025_28 || exit 1
python -u olmo32/score_ll.py --model /workspace/models/dpo --tokenizer /workspace/models/tok --name dpo \
  --items $A/ll/items.jsonl --out $A/ll/scores_dpo.jsonl > $A/ll/score_dpo.log 2>&1; rc=$?
tail -n 1 $A/ll/score_dpo.log
echo "JOB_DONE L_dpo rc=$rc $(date -u +%FT%TZ)"; [ $rc -eq 0 ] && touch $A/meta/L_dpo.done
