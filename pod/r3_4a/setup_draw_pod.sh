#!/usr/bin/env bash
# local helper: prepare a fresh pod and run one full draw on it (Stage-1 -> arms -> b10k). usage: setup_draw_pod.sh <pod> <size> <seed> <cfg> <ft_lr>
P=$1; SZ=$2; S=$3; CFG=$4; FTLR=$5
TAG=${SZ}_s$S; [ "$CFG" = B ] && TAG=${SZ}B_s$S
cd /home/dan/work/round3-run4a
bash pod/r3_4a/sync.sh $P >/dev/null
timeout 110 podrun $P "pip install -q -U --break-system-packages huggingface_hub 2>&1 | grep -v WARNING | tail -1; hf buckets cp hf://buckets/dan-pandori/nd-rl/round3-run4a/data/r3_4a/train_reductio_f0_b1.jsonl data/r3_4a/train_reductio_f0_b1.jsonl 2>&1 | tail -1; md5sum data/r3_4a/train_reductio_f0_b1.jsonl"
timeout 12 podrun $P "setsid nohup bash pod/r3_4a/stage1.sh $SZ $S $CFG > artifacts/r3_4a/stage1_$TAG.out 2>&1 < /dev/null & disown; sleep 1; echo stage1 $TAG"
timeout 12 podrun $P "setsid nohup bash pod/r3_4a/queue2.sh $FTLR 1024 cov,ei,frozen $TAG:$S > artifacts/r3_4a/queue2_$TAG.out 2>&1 < /dev/null & disown; sleep 1; echo arms $TAG"
timeout 12 podrun $P "setsid nohup bash pod/r3_4a/b10k_queue.sh frozen_$TAG.done 2000 $TAG > artifacts/r3_4a/b10k_queue_$TAG.out 2>&1 < /dev/null & disown; sleep 1; echo b10k $TAG"
