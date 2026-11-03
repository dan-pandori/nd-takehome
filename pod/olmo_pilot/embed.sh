#!/usr/bin/env bash
cd /workspace/nd-takehome
CUDA_VISIBLE_DEVICES="" nice -n 19 python olmo_pilot/nearest_embed.py data/olmo_pilot/dolci_rl_zero_math_7b_93b5e498.parquet olmo_pilot/problems.jsonl artifacts/olmo_pilot/contam/nearest_embed.csv
echo EMBED_DONE
