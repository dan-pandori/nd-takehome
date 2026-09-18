#!/usr/bin/env bash
# round3-run4a arms for one draw: pre-RL coverage (k=2000, 300 targets) -> EI (8 x 32) -> frozen twin. Resumable via .done markers.
# usage: bash pod/r3_4a/arms.sh <tag e.g. m85_s0> <seed> <ft_lr> <sample batch> [stages: cov,ei,frozen]
set -e
cd /workspace/nd-takehome
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
export OMP_NUM_THREADS=${OMP_NUM_THREADS:-1} MKL_NUM_THREADS=1   # pods have a ~13-CPU cgroup quota on a 256-core host; torch defaults to 256 threads
TAG=$1; S=$2; FTLR=$3; B=$4; STAGES=${5:-cov,ei,frozen}
CK=ckpts/r3_4a/stage1_reductio_f0_b1_$TAG.pt
A=artifacts/r3_4a
T=data/p2/targets_reductio_req.jsonl; TR=data/p2/transfer_reductio_req.jsonl
for st in ${STAGES//,/ }; do
  [ -f $A/${st}_$TAG.done ] && continue
  case $st in
    cov)    python3 coverage.py --ckpt $CK --in $T --out $A/cov_${TAG}_pre --k 2000 --temperature 0.8 --seed 0 --batch 2000 --procs 8 --lenfield min_lines_ub > $A/cov_${TAG}_pre.log 2>&1;;
    ei)     python3 expert_iter.py --init $CK --name r3_4a/ei_$TAG --targets $T --transfer $TR --heldout data/p2/heldout.jsonl --train data/r3_4a/train_reductio_f0_b1.jsonl \
              --rounds 8 --k 32 --temperature 0.8 --retain 20000 --max_per_thm 4 --ft_steps 600 --ft_lr $FTLR --seed $S --batch $B > $A/ei_$TAG.log 2>&1
            # keep only the final EI checkpoint on the pod's 20 GB disk
            ls ckpts/r3_4a/ei_${TAG}_r*.pt 2>/dev/null | sort -V | head -n -1 | xargs -r rm -f;;
    frozen) python3 expert_iter.py --init $CK --name r3_4a/frozen_$TAG --targets $T --transfer $TR --heldout data/p2/heldout.jsonl --train data/r3_4a/train_reductio_f0_b1.jsonl \
              --rounds 8 --k 32 --temperature 0.8 --retain 20000 --max_per_thm 4 --seed $S --batch $B --no_train > $A/frozen_$TAG.log 2>&1;;
  esac
  touch $A/${st}_$TAG.done
done
