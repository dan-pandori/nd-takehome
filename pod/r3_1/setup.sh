#!/usr/bin/env bash
# Local: sync code + push data to a round3-run1 pod. Usage: bash pod/r3_1/setup.sh <pod> [depth3|reductio|both]
P=$1; W=${2:-both}; R=/home/dan/work/round3-run1; cd $R
bash pod/r3_1/wpod.sh sync $P
for f in data/heldout.jsonl data/transfer.jsonl data/p2/heldout.jsonl data/p2/targets_depth3.jsonl data/p2/targets_depth3_maxdepth2.jsonl data/p2/transfer_depth3.jsonl data/p2/targets_reductio_req.jsonl data/p2/transfer_reductio_req.jsonl data/r3_1/; do bash pod/r3_1/wpod.sh push $P $f; done
[ "$W" != reductio ] && bash pod/r3_1/wpod.sh push $P data/p2/train_depth3_f0_a1.jsonl
[ "$W" != depth3 ] && bash pod/r3_1/wpod.sh push $P data/p2/train_reductio_f0.jsonl
podrun $P "ls data/p2 data/r3_1 | tr '\n' ' '; nvidia-smi --query-gpu=name,memory.total --format=csv,noheader; nproc"
