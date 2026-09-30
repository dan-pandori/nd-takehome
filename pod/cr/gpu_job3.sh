#!/bin/bash
# compute-record GPU check, part 3 (after review fixes): fast_train counting per step (the CUDA-graph path CI cannot
# run), and grpo.py's phases (sample / update / eval per round; attempts; update-only train_steps).
export ND_RUN_ID=compute-record ND_REGISTRY_DIR=artifacts/compute-record/registry PYTHONUNBUFFERED=1
O=artifacts/compute-record/gpu; mkdir -p $O ckpts/cr
w() { name=$1; shift; t0=$(date +%s.%N); "$@" > $O/$name.log 2>&1; rc=$?; t1=$(date +%s.%N)
      echo "{\"job\": \"$name\", \"t0\": $t0, \"t1\": $t1, \"rc\": $rc}" >> $O/walls.jsonl; }
[ -f ckpts/cr/fast_s0.pt ] || hf buckets cp hf://buckets/dan-pandori/nd-rl/compute-record/ckpts/cr/fast_s0.pt ckpts/cr/fast_s0.pt
w train_fast_perstep python3 train.py --data data/lj/train_retain.jsonl --mode lean_seq --cap 0 --bs 500 --seed 2 --steps 600 \
  --log_every 600 --out ckpts/cr/fast_s2.pt
LEAN_GATE_LOG=$O/grpo_gate.jsonl w grpo python3 grpo.py --init ckpts/cr/fast_s0.pt --name cr_grpo --targets data/lj/heldout200.jsonl \
  --transfer data/lj/transfer50.jsonl --heldout data/lj/targets200.jsonl --rounds 2 --k 8 --eval_k 4 --max_new 288 --batch 4096
echo JOB DONE > $O/DONE3
