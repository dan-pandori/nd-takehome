#!/usr/bin/env bash
# Regenerate every label file, summary and theorem-level file of run proof-strategies from the inputs (VPS, ≈ 6 min,
# one process at a time).  Inputs: data/ps/in/ (copied, see data/ps/README.md), data/ladder/, data/bs/, and the
# Lean-checked search outputs data/ps/search/*.checked.jsonl (pod jobs J1–J3, log.md 2026-10-18).
set -euo pipefail
cd "$(dirname "$0")/.."
L=artifacts/ps/labels; S=artifacts/ps/summary; T=artifacts/ps/theorem; mkdir -p $L $S $T
cls() { python3 proof_strategies/strategies.py --in "$1" --out $L/$2.jsonl.gz; }
cls data/ps/in/train_k12.jsonl.gz k12
cls data/ps/in/train_depth3_f0_a1.jsonl.gz cap6
cls data/ps/in/train_k12ko.jsonl.gz k12ko
cls data/ps/in/train_k12dose1.jsonl.gz k12dose1      # create-or-elicit's 1 % dose set (K12⁻ + 1,550 σ⁺ records)
cls data/ladder/rl_targets.jsonl rl_targets_gen          # the 760 textbook-schema rows have no proof (parse_fail rows)
cls data/ladder/transfer.jsonl transfer_gen
cls data/bs/holdout250.jsonl holdout250_gen
cls data/ps/in/charles/charles_base_full.jsonl charles_base
cls data/ps/search/k12_min990.checked.jsonl k12_min990
cls data/ps/search/tb_schema.checked.jsonl tb_schema_search
cls data/ps/search/textbook72.checked.jsonl textbook72_search   # scoring only: labels, never theorem text
for s in k12 cap6 k12ko k12dose1 rl_targets_gen transfer_gen holdout250_gen charles_base k12_min990; do
  python3 proof_strategies/summarize.py --labels $L/$s.jsonl.gz --name $s --out $S/$s.json > /dev/null; done
python3 proof_strategies/summarize.py --labels $L/tb_schema_search.jsonl.gz --name tb_schema --out $S/tb_schema.json > /dev/null
python3 proof_strategies/summarize.py --labels $L/textbook72_search.jsonl.gz --name textbook72 --out $S/textbook72.json > /dev/null
for s in rl_targets transfer holdout250; do
  python3 -c "
import json
for i, l in enumerate(open('data/ps/pod/tb_schema.jsonl')):
    if json.loads(l)['set'] == '$s': print(i)" > /tmp/ps_keep_$s.txt
  python3 proof_strategies/summarize.py --labels $L/tb_schema_search.jsonl.gz --keep /tmp/ps_keep_$s.txt --name ${s}_schema --out $S/${s}_schema.json > /dev/null
done
for pair in "data/ps/in/train_k12.jsonl.gz k12" "data/ps/in/train_depth3_f0_a1.jsonl.gz cap6" "data/ps/in/train_k12ko.jsonl.gz k12ko" "data/ps/in/train_k12dose1.jsonl.gz k12dose1" \
            "data/ladder/rl_targets.jsonl rl_targets" "data/ladder/transfer.jsonl transfer" "data/bs/holdout250.jsonl holdout250" \
            "data/ps/in/charles/charles_base_full.jsonl charles_base" "data/bs/textbook72.jsonl textbook72" "data/ps/pod/tb_schema.jsonl tb_schema"; do
  set -- $pair; python3 proof_strategies/theorem_level.py --in $1 --out $T/$2.jsonl.gz; done > $T/totals.jsonl; cp $T/totals.jsonl artifacts/ps/theorem_totals.txt
python3 proof_strategies/rl_mix.py > /dev/null   # needs artifacts/ps/scratch/mix_*.jsonl.gz (bucket, see rl_mix.py)
echo run_all done
