#!/usr/bin/env bash
# KAL-D sampled reads at batch 1,024 (2,048 OOMs a 48 GB card on KAL-D's long attempts), then optional extra jobs.
# Usage: bash pod/kal/queue_D.sh <seed> [check]   -- "check": afterwards re-read KAL-C s0 and control s0 (plain k 32) at
# batch 1,024, to measure the batch effect against their batch-2,048 reads.
cd /workspace/nd-takehome; . pod/kal/env.sh
S=$1
B=1024 bash pod/kal/queue_sampled.sh kal:kalD_s$S=ckpts/kalmar/stage1_kalD_s$S.pt
if [ "$2" = check ]; then
  E=artifacts/kalmar/eval; K=data/kalmar
  SETS=data/bs/holdout250.jsonl,data/ladder/transfer_long_rr600.jsonl,data/ladder/transfer_long_ge17.jsonl,data/ladder/transfer_long2.jsonl,data/gt/candidate_v0.jsonl,data/gt/candidate_v1.jsonl,data/gt/batch3.jsonl,data/gt/hand_proved_14.jsonl,data/bs/textbook72.jsonl,$K/g1_premises.jsonl,$K/g2_large.jsonl,$K/g3_classical.jsonl
  for spec in kalC_s0=ckpts/kalmar/stage1_kalC_s0.pt:kalmar-pretrain ctl_s0=ckpts/ctl/stage1_best12_s0_b1200.pt:best-state; do
    T=${spec%%=*}; R=${spec#*=}; C=${R%%:*}; RUN=${R#*:}
    mkdir -p $(dirname $C)
    SRC=$BK/$RUN/$C; [ $RUN = best-state ] && SRC=$BK/best-state/ckpts/bs/$(basename $C)
    until [ -s $C ]; do hf buckets cp $SRC $C > /dev/null 2>&1 || sleep 60; done
    python3 guided_eval.py --ckpt $C --arm plain --k 32 --seed 1 --sets $SETS --out $E/${T}_plain_k32_b1024 --max_steps 1024 --max_action 512 --batch 1024 > artifacts/kalmar/logs/plain32b1024_$T.log 2>&1
  done
  up artifacts/kalmar/eval; up artifacts/kalmar/logs
fi
touch artifacts/kalmar/markers/queue_D_s$S.done
