#!/usr/bin/env bash
# Phase 0.2, same-workload GPU-class comparison: trajectory's ladder round 1 (pend sampling the 4,495 rl_targets at k 32,
# batch 2,048, seed S*1000+1, then the eval phase) re-run on THIS pod's GPU with --no_train, alone on the card.
# trajectory's round-1 phase seconds on RTX A6000 are in its registry rows (sample: s0 1,155.9 s, s1 1,174.4 s).
# Usage: bash pod/coe/replica.sh <seed>
source pod/coe/env.sh
S=$1; mkdir -p ckpts/coe/old
CK=ckpts/coe/old/stage1_best12_s${S}_b1200.pt
[ -s $CK ] || hf buckets cp $BK/trajectory/ckpts/tj/stage1_best12_s${S}_b1200.pt $CK >/dev/null 2>&1
md5sum $CK
ND_ARM=replica_r1 ND_SEED=$S python3 state_ladder_ei.py --init $CK --name rep_best12_s$S --seed $S --batch 2048 --rounds 1 --no_train \
  --train data/kh/train_k12.jsonl --heldout data/p2/heldout.jsonl --outdir artifacts/coe/replica --ckptdir ckpts/coe/replica
python3 -c "import json;d=json.load(open('artifacts/coe/replica/rep_best12_s$S/round_1.json'));print('replica s$S round 1 secs', round(d['secs'],1), 'targets solved', d['targets_cum']['solved'], 'acc', round(d['target_sample_acc'],4))"
up artifacts/coe/replica
