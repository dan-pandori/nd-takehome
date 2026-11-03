#!/usr/bin/env bash
# Phase L: teacher-forced log-likelihood of the selected correct solutions (artifacts/olmo_pilot/ll/sel_<model>.txt)
# under the base and under the checkpoint that generated them. No sampling.
cd /workspace/nd-takehome; A=artifacts/olmo_pilot; M=/workspace/models; RL=allenai/Olmo-3.1-7B-RL-Zero-Math
bash pod/olmo_pilot/fetch.sh allenai/Olmo-3-1025-7B main base_tok tokenizer.json tokenizer_config.json special_tokens_map.json vocab.json merges.txt config.json
cat $A/ll/sel_*.txt | grep '|' > $A/ll/sel_all.txt
python olmo_pilot/ll_items.py --keys $A/ll/sel_all.txt --jobs x --tokenizer $M/base_tok --out $A/ll/L_items_all.jsonl
bash pod/olmo_pilot/fetch.sh allenai/Olmo-3-1025-7B main base
python olmo_pilot/score_ll.py --model $M/base --tokenizer $M/base_tok --name base --items $A/ll/L_items_all.jsonl --out $A/ll/L_scored_base_all.jsonl > $A/logs/L_base.log 2>&1
grep -E 'tok_per_s' $A/logs/L_base.log
for spec in "step_2800 step_2800" "step_0500 step_0500" "step_0100 step_0100"; do
  set -- $spec; m=$1
  [ -s $A/ll/sel_$m.txt ] || continue
  python olmo_pilot/ll_items.py --keys $A/ll/sel_$m.txt --jobs x --tokenizer $M/base_tok --out $A/ll/L_items_$m.jsonl
  bash pod/olmo_pilot/fetch.sh $RL $2 $m
  python olmo_pilot/score_ll.py --model $M/$m --tokenizer $M/base_tok --name $m --items $A/ll/L_items_$m.jsonl --out $A/ll/L_scored_${m}_own.jsonl > $A/logs/L_$m.log 2>&1
  grep -E 'tok_per_s' $A/logs/L_$m.log
done
echo "LL_DONE $(date -u +%FT%TZ)"
