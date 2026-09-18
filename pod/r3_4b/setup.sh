#!/usr/bin/env bash
# Local: sync code + push data to a round3-run4b pod. Usage: bash pod/r3_4b/setup.sh <pod>
P=$1; cd /home/dan/work/round3-run4b
bash pod/r3_4b/wpod.sh sync $P
for f in data/p2/heldout.jsonl data/p2/train_depth3_f0_a1.jsonl data/p2/targets_depth3.jsonl data/r3_1/; do bash pod/r3_4b/wpod.sh push $P $f; done
podrun $P "ls data/p2 data/r3_1 | tr '\n' ' '; nvidia-smi --query-gpu=name,memory.total --format=csv,noheader; nproc; free -g | sed -n 2p; python3 -c 'import torch; print(torch.__version__, torch.cuda.is_available())'"
