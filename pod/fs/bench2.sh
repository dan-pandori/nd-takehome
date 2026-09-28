#!/usr/bin/env bash
# Timing pass 2: fast path with the whole step as a CUDA graph; default vs max-autotune compile; 1,000 steps, seed 0.
cd /workspace/nd-takehome; export OMP_NUM_THREADS=4
D=data/p2/train_depth3_f0_a1.jsonl; H=data/p2/heldout.jsonl; C="--mode lean_seq --steps ${STEPS:-1000} --bs 128 --cap 6 --seed 0 --val_bins --log_every 200"
for v in ${VARIANTS:-graph}; do
  case $v in
    graph) E=""; X="" ;;
    graph_mat) E="ND_COMPILE_MODE=max-autotune-no-cudagraphs"; X="" ;;
    nograph) E=""; X="--no_graph" ;;
  esac
  rm -f artifacts/fs/b2_$v.jsonl
  env $E TORCH_LOGS=recompiles python3 train.py --data $D --heldout $H $C --impl fast $X --out ckpts/fs/b2_$v.pt --metrics artifacts/fs/b2_$v.jsonl > artifacts/fs/logs/b2_$v.log 2>&1
done
