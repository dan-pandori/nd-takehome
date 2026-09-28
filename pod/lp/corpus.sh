#!/usr/bin/env bash
# lean-prefilter C1: shadow-mode sampling from 8 checkpoints (the soundness corpus).  Usage: bash pod/lp/corpus.sh [N parallel]
cd /workspace/nd-takehome; mkdir -p artifacts/lp/corpus artifacts/lp/logs
export PATH=$HOME/.elan/bin:$PATH OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True LEAN_PREFILTER=shadow
P=${1:-2}; i=0
for ck in ckpts/lp/*.pt; do
  n=$(basename $ck .pt)
  [ -e artifacts/lp/logs/corpus_$n.log ] && continue
  LEAN_GATE_LOG=artifacts/lp/corpus/$n.gate.jsonl LEAN_GATE_DUMP=artifacts/lp/corpus/$n.dump.jsonl \
    python3 -u lp_corpus.py --ckpt $ck --name $n --seed $i > artifacts/lp/logs/corpus_$n.log 2>&1 &
  i=$((i+1))
  while [ $(jobs -rp | wc -l) -ge $P ]; do sleep 20; done
done
wait; echo "CORPUS DONE $(date -u +%FT%TZ)"
